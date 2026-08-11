from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status

import src.rbac.repository as repository
from src.rbac.models import Role, RolePermission, Permission
from src.rbac.constants import ErrorMessage
from src.rbac.schemas import UpdateRole

async def add_role(
    db: AsyncSession,
    role_name: str
) -> Role:

    if not role_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.MISSING_ROLE_NAME
        )

    if await repository.get_role_by_name(db=db, role_name=role_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.ROLE_NAME_EXIST
        )

    role = Role(name=role_name)

    role = await repository.add_role(db=db, role=role)

    if role:
        await db.commit()
        return role

async def update_role(
    db: AsyncSession,
    role_id: int,
    role_data: UpdateRole
) -> Role: 

    role = await get_role_by_id(db=db, role_id=role_id)

    if not role_data.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.MISSING_ROLE_NAME
        )

    role.name = role_data.name

    await db.commit()
    await db.refresh(role)

    return role

async def delete_role(
    db: AsyncSession,
    role_id: int
) -> None:

    _ = await get_role_by_id(db=db, role_id=role_id)

    if not await repository.delete_role(db=db, role_id=role_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.ROLE_DELETE_ERROR
        )

    await db.commit()

async def add_permission_to_role(
    db: AsyncSession,
    role_id: int,
    permission_id: int
) -> RolePermission:

    _ = await get_role_by_id(db=db, role_id=role_id)

    permission = await repository.get_permission_by_id(db=db, permission_id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.PERMISSION_NOT_FOUND
        )

    if await repository.role_has_permission(
        db=db,
        role_id=role_id,
        permission_code=permission.code
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.ROLE_PERMISSION_EXIST
        )

    role_permission = RolePermission(
        role_id=role_id,
        permission_id=permission_id
    )

    role_permission = await repository.add_permission_to_role(db=db, role_permission=role_permission)
    if role_permission:
        await db.commit()
        return role_permission

async def get_role_by_id(
    db: AsyncSession,
    role_id: int,  
) -> Role:

    role = await repository.get_role_by_id(db=db, role_id=role_id)
    if not role:
       raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.ROLE_NOT_FOUND
        )
    return role

async def get_roles(
    db: AsyncSession, 
) -> list[Role]:
    return await repository.get_roles(db=db)

async def get_role_permissions(
    db: AsyncSession,
    role_id: int
) -> list[Permission]:
    role = await get_role_by_id(db=db, role_id=role_id)
    return await repository.get_role_permissions(db=db, role=role)

async def get_permissions(
    db: AsyncSession,      
) -> list[Permission]:
    return await repository.get_permissions(db=db)

async def get_permission_by_id(
    db: AsyncSession,
    permission_id: int
) -> list[Permission]:
    permission = await repository.get_permission_by_id(db=db, permission_id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessage.PERMISSION_NOT_FOUND
        )
    return permission