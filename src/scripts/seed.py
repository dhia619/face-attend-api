import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import hash_password
from src.config import get_settings
from src.database import db_session, engine
from src.users.models import User
from src.rbac.models import Role, Permission, RolePermission
from src.rbac.constants import PermissionCode, RoleName
from src.core.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

PERMISSIONS = (
    PermissionCode.USERS_READ,
    PermissionCode.USERS_WRITE,
    PermissionCode.EMPLOYEES_READ,
    PermissionCode.EMPLOYEES_WRITE,
    PermissionCode.ATTENDANCE_READ,
    PermissionCode.ATTENDANCE_WRITE,
    PermissionCode.DEVICES_READ,
    PermissionCode.DEVICES_WRITE,
    PermissionCode.REPORTS_READ,
)

ROLES = [
    {
        "name": RoleName.SUPER_ADMIN,
        "permissions": [
            PermissionCode.USERS_READ,
            PermissionCode.USERS_WRITE,
            PermissionCode.EMPLOYEES_READ,
            PermissionCode.EMPLOYEES_WRITE,
            PermissionCode.ATTENDANCE_READ,
            PermissionCode.ATTENDANCE_WRITE,
            PermissionCode.DEVICES_READ,
            PermissionCode.DEVICES_WRITE,
            PermissionCode.REPORTS_READ,
        ]
    },
]


async def seed_permissions(db: AsyncSession) -> dict[str, Permission]:
    """Insert permissions if they don't exist."""
    result = await db.execute(select(Permission))
    existing = [p.code for p in result.scalars().all()]

    for permission_code in PERMISSIONS:
        if permission_code not in existing:
            perm = Permission(code=permission_code)
            db.add(perm)
            logger.info(f"Created permission: {permission_code}")
        else:
            logger.info(f"Permission already exists, skipping: {permission_code}")

    await db.flush()

    result = await db.execute(select(Permission))
    return {p.code: p.id for p in result.scalars().all()}


async def seed_roles(db: AsyncSession, permissions: dict[str, Permission]) -> dict[str, Role]:
    """Insert roles and wire their permissions if they don't exist."""
    result = await db.execute(select(Role))
    existing = [r.name for r in result.scalars().all()]

    for role_data in ROLES:
        if role_data["name"] not in existing:
            role = Role(name=role_data["name"])
            db.add(role)
            await db.flush()

            for code in role_data["permissions"]:
                permission_id = permissions.get(code)
                if permission_id:
                    db.add(RolePermission(role_id=role.id, permission_id=permission_id))

            logger.info(f"Created role: {role_data['name']}")
        else:
            logger.info(f"Role already exists, skipping: {role_data['name']}")

    await db.flush()

    result = await db.execute(select(Role))
    return {r.name: r.id for r in result.scalars().all()}


async def seed_super_admin(db: AsyncSession, roles: dict[str, Role]) -> None:
    result = await db.execute(select(User).where(User.email == settings.FIRST_ADMIN_EMAIL))
    if result.scalar_one_or_none():
        logger.info("Super admin already exists, skipping.")
        return

    super_admin_role_id = roles.get(RoleName.SUPER_ADMIN)
    if not super_admin_role_id:
        logger.error("super_admin role not found — cannot create super admin.")
        return

    admin = User(
        full_name="Super Admin",
        email=settings.FIRST_ADMIN_EMAIL,
        password_hash=hash_password(settings.FIRST_ADMIN_PASSWORD),
        role_id=super_admin_role_id,
        is_active=True,
    )
    db.add(admin)
    logger.info("Super admin created successfully.")


async def main():
    try:
        async with db_session() as db:
            permissions = await seed_permissions(db)
            roles = await seed_roles(db, permissions)
            await seed_super_admin(db, roles)
            await db.commit()
            logger.info("Seeding completed successfully.")
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())