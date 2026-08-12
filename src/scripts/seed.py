import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import hash_secret
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
    PermissionCode.ROLE_READ,
    PermissionCode.ROLE_WRITE,
    PermissionCode.PERMISSION_READ,
    PermissionCode.DEPARTMENT_READ,
    PermissionCode.DEPARTMENT_WRITE,
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
        "permissions": PERMISSIONS
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


async def seed_roles(
    db: AsyncSession,
    permissions: dict[str, int],
) -> dict[str, int]:
    """Insert roles and wire their permissions if they don't exist."""
    result = await db.execute(select(Role))
    roles_by_name = {
        role.name: role
        for role in result.scalars().all()
    }

    for role_data in ROLES:
        role_name = role_data["name"]

        role = roles_by_name.get(role_name)

        if role is None:
            role = Role(name=role_name)
            db.add(role)
            await db.flush()

            roles_by_name[role_name] = role
            logger.info(f"Created role: {role_name}")
        else:
            logger.info(f"Role already exists: {role_name}")

        result = await db.execute(
            select(RolePermission.permission_id)
            .where(RolePermission.role_id == role.id)
        )

        existing_permission_ids = set(result.scalars().all())

        for code in role_data["permissions"]:
            permission_id = permissions.get(code)

            if permission_id is None:
                logger.warning(
                    f"Permission not found: {code}"
                )
                continue

            if permission_id not in existing_permission_ids:
                db.add(
                    RolePermission(
                        role_id=role.id,
                        permission_id=permission_id,
                    )
                )

                logger.info(
                    f"Assigned permission {code} to role {role_name}"
                )

    await db.flush()

    return {
        name: role.id
        for name, role in roles_by_name.items()
    }


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
        password_hash=hash_secret(settings.FIRST_ADMIN_PASSWORD),
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