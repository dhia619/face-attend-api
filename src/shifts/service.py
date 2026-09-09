from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException, status

from typing import Any

import src.shifts.repository as repository
from src.shifts.models import Shift
from src.shifts.constants import ErrorMessage
from src.shifts.schemas import ShiftCreate, ShiftUpdate
from src.config import get_settings
from src.departments.constants import ErrorMessage as DepartmentErrorMessage

settings = get_settings()

async def add_shift(
    db: AsyncSession,
    shift_data: ShiftCreate
) -> Shift:

    if await get_shift_by_department(db, shift_data.department_id):
        raise HTTPException(
            detail=ErrorMessage.DEPARTMENT_SHIFT_ALREADY_EXISTS,
            status_code=status.HTTP_409_CONFLICT
        )
    try:
        shift = await repository.add_shift(db, shift_data)
        await db.commit()
    except IntegrityError:
        raise HTTPException(
            detail=DepartmentErrorMessage.DEPARTMENT_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND
        )

    return shift

async def update_shift(
    db: AsyncSession,
    shift_id: int,
    shift_data: ShiftUpdate,
) -> Shift:

    shift = await get_shift_by_id(db, shift_id)
    return await repository.update_shift(db, shift, shift_data)
    
async def delete_shift(
    db: AsyncSession,
    shift_id: int
) -> None:

    await get_shift_by_id(db, shift_id)
    if await repository.delete_shift(db, shift_id):
        await db.commit()


async def get_shift_by_id(
    db: AsyncSession,
    shift_id: int,
) -> Shift:

    shift = await repository.get_shift_by_id(db, shift_id)
    if not shift:
        raise HTTPException(
            detail=ErrorMessage.SHIFT_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND
        )
    return shift

async def get_shift_by_department(
    db: AsyncSession,
    department_id: int
) -> Shift:

    return await repository.get_shift_by_department(db, department_id)

async def list_shifts(
    db: AsyncSession,
    page: int = 1,
    page_size: int = settings.PAGINATION_PAGE_SIZE
) -> dict[str, Any]:

    shifts = await repository.list_shifts(
        db=db,
        page=page,
        page_size=page_size,
        limit=page_size + 1,
    )

    return {
        "shifts": shifts[:page_size],
        "page": page,
        "page_size": page_size,
        "has_next": len(shifts) > page_size,
    }