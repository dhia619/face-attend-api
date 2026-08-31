from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.rbac.schemas import *
import src.rbac.service as service
from src.users.models import User
from src.rbac.dependencies import require_permission
from src.rbac.constants import PermissionCode
from src.config import get_settings

settings = get_settings()

rbac_router = APIRouter()

@rbac_router.get("/roles", response_model=ListRolesResponse)
async def list_roles(
    page: int = Query(1),
    page_size: int = Query(settings.PAGINATION_PAGE_SIZE),
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.ROLE_READ))
):
    return await service.list_roles(
        db=session,
        page=page,
        page_size=page_size
    )


@rbac_router.get("/roles/all", response_model=list[RoleRead])
async def list_roles(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.ROLE_READ))
):
    return await service.get_all_roles(session)


@rbac_router.get("/roles/{role_id}", response_model=RoleRead)
async def get_role(
    role_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.ROLE_READ))
):
    return await service.get_role_by_id(db=session, role_id=role_id)


@rbac_router.post(
    "/roles", 
    response_model=RoleRead, 
    status_code=status.HTTP_201_CREATED
)
async def create_role(
    role_data: CreateRole,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.ROLE_WRITE))
):
    return await service.add_role(
        db=session,
        role_data=role_data
    )

@rbac_router.post(
    "/roles/{role_id}/permissions"
)
async def assign_permissions_to_role(
    role_id: int,
    payload: AssignPermissions,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.ROLE_WRITE))
):
    await service.add_permissions_to_role(
        db=session,
        role_id=role_id,
        permission_ids=payload.permission_ids
    )

@rbac_router.put("/roles/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: int,
    role_data: UpdateRole,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.ROLE_WRITE))
):
    return await service.update_role(
        db=session,
        role_id=role_id,
        role_data=role_data
    )


@rbac_router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.ROLE_WRITE))
):
    await service.delete_role(db=session, role_id=role_id)


@rbac_router.get("/roles/{role_id}/permissions", response_model=list[PermissionRead])
async def list_role_permissions(
    role_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.ROLE_READ)),
    user: User = Depends(require_permission(PermissionCode.PERMISSION_READ))
):
    return await service.get_role_permissions(db=session, role_id=role_id)


@rbac_router.get("/permissions", response_model=list[PermissionRead])
async def list_permissions(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.PERMISSION_READ))
):
    return await service.get_permissions(db=session)


@rbac_router.get("/permissions/{permission_id}", response_model=PermissionRead)
async def get_permission(
    permission_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.PERMISSION_READ))
):
    return await service.get_permission_by_id(db=session, permission_id=permission_id)