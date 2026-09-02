from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Any

from src.employees.models import Employee, FaceEmbedding
from src.employees.schemas import UpdateEmployee
from src.shared.pagination import get_page_offset

async def get_employee_by_email(
    db: AsyncSession,
    email: str,
) -> Employee | None:
    result = await db.execute(select(Employee).where(Employee.email == email))
    return result.scalar_one_or_none()

async def get_employee_by_id(
    db: AsyncSession,
    employee_id: int,
) -> Employee | None:
    return await db.get(Employee, employee_id)

async def get_employees(
    db: AsyncSession,
    page: int,
    page_size: int,
    limit: int | None = None,
) -> list[Employee]:
    fetch_limit = limit if limit is not None else page_size
    result = await db.execute(
        select(Employee)
        .order_by(Employee.id)
        .offset(get_page_offset(page, page_size))
        .limit(fetch_limit)
    )
    return list(result.scalars().all())

async def add_employee(
    db: AsyncSession,
    employee: Employee,
    face_embedding: FaceEmbedding,
) -> Employee:
    
    employee.face_embedding = face_embedding

    db.add(employee)
    await db.flush()
    await db.refresh(employee)

    return employee

async def update_employee(
    db: AsyncSession,
    employee: Employee,
    employee_data: UpdateEmployee,
) -> Employee:

    data = employee_data.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(employee, field, value)

    await db.flush()

    return employee

async def update_face_embedding(
    db: AsyncSession,
    employee: Employee,
    embeddings: list[float],
) -> FaceEmbedding:
    if employee.face_embedding is None:
        employee.face_embedding = FaceEmbedding(
            embeddings=embeddings
        )
    else:
        employee.face_embedding.embeddings = embeddings

    await db.flush()

    return employee.face_embedding

async def delete_employee(
    db: AsyncSession,
    employee_id: int,
) -> bool:
    
    result = await db.execute(delete(Employee).where(Employee.id == employee_id))
    return result.rowcount == 1

async def find_closest_employee(
    db: AsyncSession,
    embedding: list[float],
    distance_threshold: float,
) -> dict[str, Any] | None:

    distance = FaceEmbedding.embeddings.cosine_distance(embedding).label("distance")

    stmt = (
        select(Employee, distance)
        .join(
            FaceEmbedding,
            FaceEmbedding.employee_id == Employee.id,
        )
        .where(distance < distance_threshold)
        .order_by(distance)
        .limit(1)
    )

    result = await db.execute(stmt)

    row = result.one_or_none()
    
    if row is None:
        return None

    employee, actual_distance = row

    return {
        "employee": employee,
        "distance": actual_distance
    }

async def get_all_active_employees(
    db: AsyncSession,
    department_id: int | None = None
) -> list[Employee]:
    query = select(Employee).where(Employee.is_active == True).options(
        selectinload(Employee.department)
    )

    if department_id:
        query = query.where(Employee.department_id == department_id)

    result = await db.execute(query)
    return list(result.scalars().all())