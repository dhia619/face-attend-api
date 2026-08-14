from datetime import datetime, timedelta, date, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.attendance.models import AttendanceRecord
from src.attendance.repository import *

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