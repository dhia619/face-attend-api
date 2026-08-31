from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status

from typing import Any

import src.departments.repository as repository
from src.departments.models import Department
from src.departments.constants import ErrorMessage
from src.departments.schemas import CreateDepartment
from src.config import get_settings

settings = get_settings()

async def add_department(
    db: AsyncSession,
    department_data: CreateDepartment
) -> Department:

    if not department_data.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.MIISING_DEPARTMENT_NAME
        )
    
    if await repository.get_department_by_name(
        db=db,
        department_name=department_data.name
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=ErrorMessage.DEPARTMENT_EXIST
        )

    department = Department(name=department_data.name)
    
    department = await repository.add_department(
        db=db,
        department=department
    )

    if department:
        await db.commit()
        return department

async def list_departments(
    db: AsyncSession,
    page: int = 1,
    page_size: int = settings.PAGINATION_PAGE_SIZE
) -> dict[str, Any]:
    """ Retrieves departments with pagination. """
    departments = await repository.list_departments(
        db=db,
        page=page,
        page_size=page_size,
        limit=page_size + 1,
    )

    return {
        "departments": departments[:page_size],
        "page": page,
        "page_size": page_size,
        "has_next": len(departments) > page_size
    }

async def get_all_departments(db: AsyncSession) -> list[Department]:
    """ Retrieves all departments without pagination. """
    return await repository.get_all_departments(db)

async def get_department(
    db: AsyncSession,
    department_id: int
) -> Department:

    department = await repository.get_department_by_id(
        db=db, 
        department_id=department_id
    )

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessage.DEPARTMENT_NOT_FOUND
        )

    return department

async def delete_department(
    db: AsyncSession,
    department_id: int
) -> None:
    
    _ = await get_department(db=db, department_id=department_id)
    
    if not await repository.delete_department(
        db=db, 
        department_id=department_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.DEPARTMENT_DELETE_ERROR
        )

    await db.commit()

async def update_department(
    db: AsyncSession,
    department_id: int,
    department_data: CreateDepartment
) -> None:

    department = await get_department(db, department_id)
    department.name = department_data.name

    await db.commit()

    return department