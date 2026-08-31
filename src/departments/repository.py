from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.departments.models import Department
from src.shared.pagination import get_page_offset
from src.config import get_settings

settings = get_settings()

async def get_department_by_id(
    db: AsyncSession,
    department_id: int
) -> Department | None:

    return await db.get(Department, department_id)

async def get_department_by_name(
    db: AsyncSession,
    department_name: str
) -> Department | None:

    result = await db.execute(select(Department).where(Department.name == department_name))
    return result.scalar_one_or_none()

async def list_departments(
    db: AsyncSession,
    page: int = 1,
    page_size: int = settings.PAGINATION_PAGE_SIZE,
    limit: int | None = None,
) -> list[Department]:
    
    result = await db.execute(
        select(Department)
        .order_by(Department.id)
        .offset(get_page_offset(page, page_size))
        .limit(limit if limit is None else page_size + 1)
    )
    return list(result.scalars().all())

async def add_department(
    db: AsyncSession,
    department: Department
) -> Department:

    db.add(department)
    await db.flush()

    return department

async def delete_department(
    db: AsyncSession,
    department_id: int
) -> bool:

    result = await db.execute(delete(Department).where(Department.id == department_id))
    return result.rowcount == 1

async def get_all_departments(db: AsyncSession) -> list[Department]:
    result = await db.execute(
        select(Department)
        .order_by(Department.name)
    )
    return list(result.scalars().all())