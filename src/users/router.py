from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.schemas import *
from src.users import service
from src.users.models import User
from src.rbac.dependencies import require_permission
from src.rbac.constants import PermissionCode
from src.dependencies import get_current_user

user_router = APIRouter()

@user_router.get("", response_model=list[UserRead])
async def list_users(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.USERS_READ))
):
    return await service.get_users(db=session)


@user_router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.USERS_READ))
):
    return await service.get_user_by_id(db=session, user_id=user_id)


@user_router.post(
    "", 
    response_model=UserRead, 
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.USERS_WRITE))
):
    return await service.register_user(
        db=session,
        user_data=user_data
    )


@user_router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.USERS_WRITE))
):
    return await service.update_user(
        db=session,
        user_id=user_id,
        user_data=payload
    )


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.USERS_WRITE))
):
    await service.delete_user(db=session, user_id=user_id)


@user_router.post("/{user_id}/change-password")
async def change_password(
    user_id: int,
    change_password_data: ChangePassword,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    await service.change_password(
        db=session,
        user_id=user_id,
        change_password_data=change_password_data
    )