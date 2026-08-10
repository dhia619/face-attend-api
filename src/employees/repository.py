from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.employees.models import Employee, FaceEmbedding
from src.employees.schemas import UpdateEmployee

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
    page_size: int
) -> list[Employee]:
    result = await db.execute(
        select(Employee)
        .order_by(Employee.id)
        .offset((page-1)*page_size)
        .limit(page_size)
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