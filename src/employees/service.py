from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from fastapi.exceptions import HTTPException
from fastapi import status

from typing import Any

from src.employees.schemas import (
    CreateEmployee, 
    UpdateEmployee, 
    CreateEmbedding, 
)
from src.employees.constants import ErrorMessage
from src.employees.models import Employee, FaceEmbedding
import src.employees.repository as repository
from src.deepface.client import get_face_embedding
from src.config import get_settings

settings = get_settings()

async def register_employee(
    db: AsyncSession,
    employee_data: CreateEmployee
) -> Employee:

    if await repository.get_employee_by_email(db=db, email=employee_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessage.EMAIL_EXISTS)

    employee = Employee(
        full_name=employee_data.full_name,
        email=employee_data.email,
        phone=employee_data.phone,
        hire_date=employee_data.hire_date,
        department_id=employee_data.department_id
    )

    face_embeddings = await get_face_embedding(employee_data.face_image)

    if not face_embeddings:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessage.FACE_EMBEDDING_FAILED)

    face_embedding = FaceEmbedding(
        embeddings = face_embeddings
    )

    try:
        employee = await repository.add_employee(
            db=db,
            employee=employee,
            face_embedding=face_embedding
        )
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessage.PHONE_EXISTS)

    if employee:
        await db.commit()
        return employee

async def get_employee_by_id(
    db: AsyncSession, 
    employee_id: int
) -> Employee:

    employee = await repository.get_employee_by_id(db=db, employee_id=employee_id)
    if not employee:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessage.EMPLOYEE_NOT_FOUND)
    return employee  

async def get_employees(
    db: AsyncSession, 
    page: int = 1,
    page_size: int = settings.PAGINATION_PAGE_SIZE
) -> dict[str, Any]:

    employees = await repository.get_employees(
        db=db,
        page=page,
        page_size=page_size,
        limit=page_size + 1,
    )

    return {
        "employees": employees[:page_size],
        "page": page,
        "page_size": page_size,
        "has_next": len(employees) > page_size,
    }

async def update_employee(
    db: AsyncSession, 
    employee_id: int,
    employee_data: UpdateEmployee
) -> Employee:

    employee = await get_employee_by_id(db=db, employee_id=employee_id)

    updated_employee = await repository.update_employee(
        db=db, 
        employee=employee,
        employee_data=employee_data
    )

    await db.commit()
    await db.refresh(updated_employee)

    return updated_employee

async def remove_employee(
    db: AsyncSession, 
    employee_id: int
) -> bool:

    await get_employee_by_id(db, employee_id)

    if await repository.delete_employee(db=db, employee_id=employee_id):
        await db.commit()
        return True
    return False

async def add_face_embedding(
    db: AsyncSession,
    employee_id: int,
    data: CreateEmbedding 
):
    await get_employee_by_id(db, employee_id)

    face_embeddings = await get_face_embedding(data.face_image)
    
    if not face_embeddings:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessage.FACE_EMBEDDING_FAILED)

    face_embedding = FaceEmbedding(
        embeddings = face_embeddings,
        employee_id = employee_id
    )

    db.add(face_embedding)
    await db.commit()