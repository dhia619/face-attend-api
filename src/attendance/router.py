from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.attendance.schemas import *
import src.attendance.service as service
from src.rbac.constants import PermissionCode
from src.dependencies import get_current_user
from src.users.models import User
from src.rbac.dependencies import require_permission
from src.config import get_settings

settings = get_settings()

attendance_router = APIRouter()


@attendance_router.get(
    "/today",
    response_model=TodayAttendanceResponse,
    dependencies=[Depends(require_permission(PermissionCode.ATTENDANCE_READ))]
)
async def get_today_attendance(
    session: AsyncSession = Depends(get_db),
    department_id: int | None = Query(None),
    user: User = Depends(get_current_user)
):
    return await service.get_today_attendance(session, department_id)