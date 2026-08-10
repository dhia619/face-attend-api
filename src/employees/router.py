from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.employees.schemas import *
import src.employees.service as service

employees_router = APIRouter()


@employees_router.get("", response_model=list[EmployeeResponse])
async def list_employees(
    session: AsyncSession = Depends(get_db)
):
    return await service.get_employees(db=session)


@employees_router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    session: AsyncSession = Depends(get_db)
):
    return await service.get_employee_by_id(db=session, employee_id=employee_id)


@employees_router.post(
    "", 
    response_model=EmployeeResponse, 
    status_code=status.HTTP_201_CREATED
)
async def create_employee(
    employee_data: CreateEmployee,
    session: AsyncSession = Depends(get_db)
):
    return await service.register_employee(
        db=session,
        employee_data=employee_data
    )


@employees_router.patch("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_data: UpdateEmployee,
    session: AsyncSession = Depends(get_db)
):
    return await service.update_employee(
        db=session,
        employee_id=employee_id,
        employee_data=employee_data
    )


@employees_router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int,
    session: AsyncSession = Depends(get_db)
):
    await service.remove_employee(db=session, employee_id=employee_id)