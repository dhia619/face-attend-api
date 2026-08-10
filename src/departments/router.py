from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.departments.schemas import *
import src.departments.service as service
from src.users.models import User
from src.rbac.dependencies import require_permission
from src.rbac.constants import PermissionCode

department_router = APIRouter()

@department_router.get("", response_model=list[DepartmentResponse])
async def list_departments(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.DEPARTMENT_READ))
):
    return await service.get_departments(db=session)


@department_router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.DEPARTMENT_READ))
):
    return await service.get_department(db=session, department_id=department_id)


@department_router.post(
    "", 
    response_model=DepartmentResponse, 
    status_code=status.HTTP_201_CREATED
)
async def create_department(
    department_data: CreateDepartment,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.DEPARTMENT_WRITE))
):
    return await service.add_department(
        db=session,
        department_data=department_data
    )


@department_router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.DEPARTMENT_WRITE))
):
    await service.delete_department(db=session, department_id=department_id)