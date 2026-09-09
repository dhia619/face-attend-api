from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_current_user
from src.users.models import User
from src.rbac.dependencies import require_permission
from src.rbac.constants import PermissionCode
from src.shifts.schemas import (
    ListShiftsResponse,
    ShiftRead,
    ShiftCreate,
    ShiftUpdate
)
import src.shifts.service as service
from src.config import get_settings

settings = get_settings()

shifts_router = APIRouter()

@shifts_router.get(
    "", 
    response_model=ListShiftsResponse,
    dependencies=[Depends(require_permission(PermissionCode.SHIFTS_READ))]
)
async def list_shifts(
    page: int = Query(1),
    page_size: int = Query(settings.PAGINATION_PAGE_SIZE),
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return await service.list_shifts(session, page, page_size)

@shifts_router.get(
    "/{shift_id}", 
    response_model=ShiftRead,
    dependencies=[Depends(require_permission(PermissionCode.SHIFTS_READ))]
)
async def get_shift(
    shift_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return await service.get_shift_by_id(session, shift_id)

@shifts_router.post(
    "", 
    response_model=ShiftRead, 
    status_code=201,
    dependencies=[Depends(require_permission(PermissionCode.SHIFTS_WRITE))]
)
async def create_shift(
    payload: ShiftCreate, 
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    return await service.add_shift(session, payload)

@shifts_router.patch(
    "/{shift_id}", 
    response_model=ShiftRead,
    dependencies=[Depends(require_permission(PermissionCode.SHIFTS_WRITE))]
)
async def update_shift(
    shift_id: int, 
    payload: ShiftUpdate, 
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    return await service.update_shift(session, shift_id, payload)

@shifts_router.delete(
    "/{shift_id}", 
    status_code=204,
    dependencies=[Depends(require_permission(PermissionCode.SHIFTS_WRITE))]
)
async def delete_shift(
    shift_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    await service.delete_shift(session, shift_id)