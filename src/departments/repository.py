from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.departments.models import Department

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

async def get_departments(
    db: AsyncSession
) -> list[Department]:
    
    result = await db.execute(select(Department))
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