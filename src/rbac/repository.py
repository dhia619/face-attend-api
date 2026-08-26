from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.rbac.models import Role, Permission, RolePermission

async def get_role_permissions(
    db: AsyncSession,
    role: Role,
) -> list[Permission]:
    result = await db.execute(
        select(Permission)
        .join(
            RolePermission,
            RolePermission.permission_id == Permission.id,
        )
        .where(RolePermission.role_id == role.id)
    )

    return list(result.scalars().all())

async def role_has_permission(
    db: AsyncSession,
    role_id: int,
    permission_code: str,
) -> bool:
    result = await db.execute(
        select(Permission.id)
        .join(
            RolePermission,
            RolePermission.permission_id == Permission.id,
        )
        .where(
            RolePermission.role_id == role_id,
            Permission.code == permission_code,
        )
        .limit(1)
    )

    return result.scalar_one_or_none() is not None

async def add_role(
    db: AsyncSession,
    role: Role
) -> Role:

    db.add(role)
    await db.flush()
    await db.refresh(role)

    return role

async def delete_role(
    db: AsyncSession,
    role_id: int
) -> bool:

    result = await db.execute(delete(Role).where(Role.id == role_id))

    return result.rowcount == 1


async def get_role_by_name(
    db: AsyncSession,
    role_name: str
) -> Role:

    result = await db.execute(select(Role).where(Role.name == role_name))

    return result.scalar_one_or_none()

async def get_role_by_id(
    db: AsyncSession,
    role_id: int
) -> Role:

    return await db.get(Role, role_id)

async def get_roles(
    db: AsyncSession 
) -> list[Role]:

    result = await db.execute(select(Role))
    return list(result.scalars().all())

async def get_permissions(
    db: AsyncSession 
) -> list[Permission]:

    result = await db.execute(select(Permission))
    return list(result.scalars().all())


async def get_permission_by_id(
    db: AsyncSession,
    permission_id: int
) -> Permission:

    return await db.get(Permission, permission_id)

async def add_permission_to_role(
    db: AsyncSession,
    role_permission: Role
) -> RolePermission:

    db.add(role_permission)
    await db.flush()

    return role_permission

async def remove_permissions_from_role(
    db: AsyncSession,
    role_id: int,
    permission_ids: list[int],
) -> None:
    if not permission_ids:
        return

    await db.execute(
        delete(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id.in_(permission_ids),
        )
    )