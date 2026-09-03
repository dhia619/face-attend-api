from datetime import datetime, timedelta, date, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from src.attendance.models import AttendanceRecord
from src.attendance.repository import *
from src.attendance.constants import CheckType
from src.attendance.schemas import AttendanceFilterParams
from src.employees.models import Employee
from src.shared.pagination import get_page_offset

async def add_attendance_record(
    db: AsyncSession,
    attendance_record: AttendanceRecord
) -> AttendanceRecord:

    db.add(attendance_record)
    await db.flush()
    await db.refresh(attendance_record)

    return attendance_record


async def get_last_record_today(
    db: AsyncSession,
    employee_id: int
) -> AttendanceRecord | None:
    """Get the most recent attendance record for this employee today"""
    today = date.today()
    result = await db.execute(
        select(AttendanceRecord)
        .where(
            AttendanceRecord.employee_id == employee_id,
            func.date(AttendanceRecord.timestamp) == today
        )
        .order_by(AttendanceRecord.timestamp.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_recent_record(
    db: AsyncSession,
    employee_id: int,
    cooldown_minutes: int = 1
) -> AttendanceRecord | None:
    """
    Check if employee was already recorded in the last N minutes.
    Prevents duplicate records when someone stands in front of camera.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=cooldown_minutes)
    result = await db.execute(
        select(AttendanceRecord)
        .where(
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.timestamp >= cutoff
        )
        .order_by(AttendanceRecord.timestamp.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()

async def get_last_records_today_bulk(
    db: AsyncSession,
    employee_ids: list[int]
) -> dict[int, AttendanceRecord]:
    """
    Most recent record today per employee.
    Used for current in/out status.
    """
    if not employee_ids:
        return {}

    today = date.today()

    result = await db.execute(
        select(AttendanceRecord)
        .where(
            AttendanceRecord.employee_id.in_(employee_ids),
            func.date(AttendanceRecord.timestamp) == today
        )
        .order_by(AttendanceRecord.employee_id, AttendanceRecord.timestamp.desc())
    )
    records = result.scalars().all()

    latest_per_employee: dict[int, AttendanceRecord] = {}
    for record in records:
        if record.employee_id not in latest_per_employee:
            latest_per_employee[record.employee_id] = record

    return latest_per_employee


async def get_first_checkins_today_bulk(
    db: AsyncSession,
    employee_ids: list[int]
) -> dict[int, AttendanceRecord]:
    """
    Earliest check_in today per employee.
    Used for lateness calculation.
    """
    if not employee_ids:
        return {}

    today = date.today()

    result = await db.execute(
        select(AttendanceRecord)
        .where(
            AttendanceRecord.employee_id.in_(employee_ids),
            AttendanceRecord.check_type == CheckType.CHECK_IN.value,
            func.date(AttendanceRecord.timestamp) == today
        )
        .order_by(AttendanceRecord.employee_id, AttendanceRecord.timestamp.asc())
    )
    records = result.scalars().all()

    first_per_employee: dict[int, AttendanceRecord] = {}
    for record in records:
        if record.employee_id not in first_per_employee:
            first_per_employee[record.employee_id] = record

    return first_per_employee


async def list_records(
    db: AsyncSession,
    filters: AttendanceFilterParams
) -> list[AttendanceRecord]:

    query = (
        select(AttendanceRecord)
        .join(Employee, AttendanceRecord.employee_id == Employee.id)
        .options(
            selectinload(AttendanceRecord.employee).selectinload(Employee.department),
            selectinload(AttendanceRecord.device),
        )
        .order_by(AttendanceRecord.timestamp.desc())
    )

    if filters.employee_id:
        query = query.where(
            AttendanceRecord.employee_id == filters.employee_id
        )

    if filters.employee_search:
        search = f"%{filters.employee_search.strip()}%"

        query = query.where(
            or_(
                Employee.full_name.ilike(search),
                Employee.email.ilike(search),
            )
        )

    if filters.department_id:
        query = query.where(
            Employee.department_id == filters.department_id
        )

    if filters.check_type:
        query = query.where(
            AttendanceRecord.check_type == filters.check_type
        )

    if filters.date_from:
        query = query.where(
            func.date(AttendanceRecord.timestamp) >= filters.date_from
        )

    if filters.date_to:
        query = query.where(
            func.date(AttendanceRecord.timestamp) <= filters.date_to
        )

    query = (
        query
        .offset(get_page_offset(filters.page, filters.page_size))
        .limit(filters.page_size + 1)
    )

    result = await db.execute(query)

    return list(result.scalars().all())