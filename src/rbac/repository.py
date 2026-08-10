from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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