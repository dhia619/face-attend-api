from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status

import src.departments.repository as repository
from src.departments.models import Department
from src.departments.constants import ErrorMessage
from src.departments.schemas import CreateDepartment

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

async def get_departments(
    db: AsyncSession  
) -> list[Department]:

    return await repository.get_departments(db)

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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.DEPARTMENT_NOT_FOUND
        )

    return department

async def delete_department(
    db: AsyncSession,
    department_id: int
) -> None:
    
    if not await repository.get_department_by_id(
        db=db,
        department_id=department_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=ErrorMessage.DEPARTMENT_NOT_FOUND
        )
    
    if not await repository.delete_department(
        db=db, 
        department_id=department_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.DEPARTMENT_DELETE_ERROR
        )

    await db.commit()