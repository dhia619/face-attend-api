from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.shifts.models import Shift

async def get_shift_for_department(db: AsyncSession, department_id: int | None) -> Shift | None:
    """
    Try department-specific shift first, fall back to default (NULL) shift.
    """
    if department_id:
        result = await db.execute(
            select(Shift).where(Shift.department_id == department_id)
        )
        shift = result.scalar_one_or_none()
        if shift:
            return shift

    result = await db.execute(
        select(Shift).where(Shift.department_id.is_(None))
    )
    return result.scalar_one_or_none()


async def get_all_shifts(db: AsyncSession) -> list[Shift]:
    result = await db.execute(select(Shift))
    return list(result.scalars().all())