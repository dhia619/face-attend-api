import logging
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from src.attendance.repository import (
    get_last_records_today_bulk
)
from src.employees.repository import get_all_active_employees
from src.attendance.constants import CheckType, AttendanceStatus
from src.attendance.schemas import TodayAttendanceResponse, EmployeeTodayStatus


async def get_today_attendance(
    db: AsyncSession,
    department_id: int | None = None
) -> TodayAttendanceResponse:

    employees = await get_all_active_employees(db, department_id)
    last_records = await get_last_records_today_bulk(
        db, employee_ids=[e.id for e in employees]
    )

    employee_statuses = []
    present_count = 0
    currently_in_count = 0
    currently_out_count = 0

    for employee in employees:
        record = last_records.get(employee.id)

        if record is None:
            is_present = False
            current_status = AttendanceStatus.NOT_ARRIVED.value
            last_seen = None
        else:
            is_present = True
            present_count += 1
            last_seen = record.timestamp
            if record.check_type == CheckType.CHECK_IN.value:
                current_status = AttendanceStatus.IN.value
                currently_in_count += 1
            else:
                current_status = CheckType.CHECK_OUT.value
                currently_out_count += 1

        employee_statuses.append(EmployeeTodayStatus(
            employee_id=employee.id,
            full_name=employee.full_name,
            department_name=employee.department.name if employee.department else None,
            is_present=is_present,
            current_status=current_status,
            last_seen_at=last_seen
        ))

    return TodayAttendanceResponse(
        date=date.today().isoformat(),
        total_employees=len(employees),
        present=present_count,
        absent=len(employees) - present_count,
        currently_in=currently_in_count,
        currently_out=currently_out_count,
        employees=employee_statuses
    )