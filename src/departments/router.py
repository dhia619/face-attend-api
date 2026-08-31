from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.departments.schemas import *
import src.departments.service as service
from src.users.models import User
from src.rbac.dependencies import require_permission
from src.rbac.constants import PermissionCode
from src.config import get_settings

settings = get_settings()

department_router = APIRouter()

@department_router.get("", response_model=ListDepartmentsResponse)
async def list_departments(
    page: int = Query(1),
    page_size: int = Query(settings.PAGINATION_PAGE_SIZE),
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.DEPARTMENT_READ))
):
    return await service.list_departments(
        db=session,
        page=page,
        page_size=page_size
    )

@department_router.get("/all", response_model=list[DepartmentRead])
async def list_all_departments(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.DEPARTMENT_READ))
):
    return await service.get_all_departments(session)


@department_router.get("/{department_id}", response_model=DepartmentRead)
async def get_department(
    department_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.DEPARTMENT_READ))
):
    return await service.get_department(db=session, department_id=department_id)


@department_router.post(
    "", 
    response_model=DepartmentRead, 
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


@department_router.put(
    "/{department_id}", 
    response_model=DepartmentRead, 
)
async def update_department(
    department_id: int,
    department_data: CreateDepartment,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.DEPARTMENT_WRITE))
):
    return await service.update_department(
        db=session,
        department_id=department_id,
        department_data=department_data
    )

@department_router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.DEPARTMENT_WRITE))
):
    await service.delete_department(db=session, department_id=department_id)