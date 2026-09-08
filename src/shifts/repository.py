from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete

from src.shifts.models import Shift
from src.shifts.schemas import ShiftCreate, ShiftUpdate
from src.shared.pagination import get_page_offset

async def get_shift_for_department(
    db: AsyncSession,
    department_id: int | None
) -> Shift | None:
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


async def list_shifts(
    db: AsyncSession,
    page: int,
    page_size: int,
    limit: int | None = None,
) -> list[Shift]:
    fetch_limit = limit if limit is not None else page_size
    result = await db.execute(
        select(Shift)
        .order_by(Shift.id)
        .offset(get_page_offset(page, page_size))
        .limit(fetch_limit)
    )
    return list(result.scalars().all())


async def get_shift_by_department(
    db: AsyncSession, 
    department_id: int
) -> Shift | None:
    result = await db.execute(
        select(Shift).where(Shift.department_id == department_id)
    )
    return result.scalar_one_or_none()


async def get_shift_by_id(
    db: AsyncSession, 
    shift_id: int
) -> Shift | None:
    result = await db.execute(
        select(Shift).where(Shift.id == shift_id)
    )
    return result.scalar_one_or_none()


async def add_shift(
    db: AsyncSession,
    shift_data: ShiftCreate
) -> Shift:
    try:
        shift = Shift(**shift_data.model_dump())
        db.add(shift)

        await db.flush()
        await db.refresh(shift)

        return shift

    except IntegrityError:
        await db.rollback()
        raise


async def update_shift(
    db: AsyncSession,
    shift: Shift,
    shift_data: ShiftUpdate,
) -> Shift:

    data = shift_data.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(shift, field, value)

    await db.flush()

    return shift


async def delete_shift(
    db: AsyncSession,
    shift_id: int
) -> bool:
    result = await db.execute(
        delete(Shift).where(Shift.id == shift_id)
    )
    return result.rowcount == 1