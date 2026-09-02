import logging
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.attendance.repository import (
    get_first_checkins_today_bulk,
    get_last_records_today_bulk
)
from src.employees.repository import get_all_active_employees
from src.shifts.repository import (
    get_all_shifts
)
from src.shifts.models import Shift
from src.attendance.models import AttendanceRecord
from src.attendance.constants import (
    AttendanceStatus,
    CheckType
)
from src.attendance.schemas import (
    TodayAttendanceResponse, 
    EmployeeTodayStatus
)
from src.employees.models import Employee

logger = logging.getLogger(__name__)

async def get_today_attendance(
    db: AsyncSession,
    department_id: int | None = None
) -> TodayAttendanceResponse:

    employees = await get_all_active_employees(db, department_id)
    employee_ids = [e.id for e in employees]

    last_records = await get_last_records_today_bulk(db, employee_ids)
    first_checkins = await get_first_checkins_today_bulk(db, employee_ids)

    shifts = await get_all_shifts(db)
    default_shift = next((s for s in shifts if s.department_id is None), None)
    shifts_by_department = {s.department_id: s for s in shifts if s.department_id is not None}

    employee_statuses: list[EmployeeTodayStatus] = []
    present_count = currently_in_count = currently_out_count = late_count = 0

    for employee in employees:
        status = _build_employee_status(
            employee=employee,
            last_record=last_records.get(employee.id),
            first_checkin=first_checkins.get(employee.id),
            shift=shifts_by_department.get(employee.department_id, default_shift)
        )
        employee_statuses.append(status)

        if status.is_present:
            present_count += 1
            if status.current_status == AttendanceStatus.IN.value:
                currently_in_count += 1
            else:
                currently_out_count += 1
        if status.is_late:
            late_count += 1

    return TodayAttendanceResponse(
        date=date.today().isoformat(),
        total_employees=len(employees),
        present=present_count,
        absent=len(employees) - present_count,
        currently_in=currently_in_count,
        currently_out=currently_out_count,
        late=late_count,
        employees=employee_statuses
    )


def _build_employee_status(
    employee: Employee,
    last_record: AttendanceRecord,
    first_checkin: AttendanceRecord,
    shift: Shift | None
) -> EmployeeTodayStatus:

    is_present = last_record is not None
    current_status = AttendanceStatus.NOT_ARRIVED
    last_seen = None

    if last_record is not None:
        last_seen = last_record.timestamp
        current_status = (
            AttendanceStatus.IN.value 
            if last_record.check_type == CheckType.CHECK_IN.value
            else AttendanceStatus.OUT.value
        )

    is_late = None
    late_minutes = None

    if first_checkin is not None and shift is not None:
        shift_start = datetime.combine(
            first_checkin.timestamp.date(),
            shift.start_time
        ).astimezone(timezone.utc)

        is_late = first_checkin.timestamp > shift_start

        if is_late:
            late_time = first_checkin.timestamp - shift_start
            late_minutes = int(late_time.total_seconds() / 60)

    return EmployeeTodayStatus(
        employee_id=employee.id,
        full_name=employee.full_name,
        department_name=employee.department.name if employee.department else None,
        is_present=is_present,
        current_status=current_status,
        last_seen_at=last_seen,
        is_late=is_late,
        late_minutes=late_minutes
    )