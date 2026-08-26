from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status

import src.rbac.repository as repository
from src.rbac.models import Role, RolePermission, Permission
from src.rbac.constants import ErrorMessage
from src.rbac.schemas import UpdateRole, CreateRole

async def add_role(
    db: AsyncSession,
    role_data: CreateRole
) -> Role:

    if await repository.get_role_by_name(db=db, role_name=role_data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ErrorMessage.ROLE_NAME_EXIST
        )

    role = Role(name=role_data.name)

    role = await repository.add_role(db=db, role=role)

    if role:
        if role_data.permission_ids:
            for p_id in role_data.permission_ids:
                if not await get_permission_by_id(db, p_id):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=ErrorMessage.PERMISSION_NOT_FOUND
                    )
                role_permission = RolePermission(
                    role_id = role.id,
                    permission_id = p_id
                )
                await repository.add_permission_to_role(
                    db=db,
                    role_permission=role_permission
                )
        await db.commit()
        return role

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorMessage.ROLE_CREATE_ERROR
    )

async def set_role_permissions(
    db: AsyncSession,
    role_id: int,
    permission_ids: list[int],
) -> None:
    await get_role_by_id(db=db, role_id=role_id)

    existing_permissions = await get_role_permissions(
        db=db,
        role_id=role_id,
    )

    existing_ids = {
        permission.id
        for permission in existing_permissions
    }

    wanted_ids = set(permission_ids)

    ids_to_add = wanted_ids - existing_ids
    ids_to_remove = existing_ids - wanted_ids

    for permission_id in ids_to_add:
        permission = await repository.get_permission_by_id(
            db=db,
            permission_id=permission_id,
        )

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessage.PERMISSION_NOT_FOUND,
            )

    await repository.remove_permissions_from_role(
        db=db,
        role_id=role_id,
        permission_ids=ids_to_remove,
    )

    for permission_id in ids_to_add:
        role_permission = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
        )

        await repository.add_permission_to_role(
            db=db,
            role_permission=role_permission,
        )

    await db.commit()

async def update_role(
    db: AsyncSession,
    role_id: int,
    role_data: UpdateRole,
) -> Role:

    role = await get_role_by_id(
        db=db,
        role_id=role_id,
    )

    suspicious_role = await repository.get_role_by_name(
        db,
        role_data.name,
    )

    if suspicious_role and suspicious_role.id != role_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ErrorMessage.ROLE_NAME_EXIST,
        )

    role.name = role_data.name

    if role_data.permission_ids is not None:
        await set_role_permissions(
            db=db,
            role_id=role.id,
            permission_ids=role_data.permission_ids
        )

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

async def get_role_by_id(
    db: AsyncSession,
    role_id: int,  
) -> Role:

    role = await repository.get_role_by_id(db=db, role_id=role_id)
    if not role:
       raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
) -> Permission:
    permission = await repository.get_permission_by_id(db=db, permission_id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessage.PERMISSION_NOT_FOUND
        )
    return permission