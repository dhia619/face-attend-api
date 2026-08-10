import logging
from fastapi import HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.dependencies import get_current_user
from src.users.models import User
from src.rbac.repository import role_has_permission
from src.rbac.constants import ErrorMessage

logger = logging.getLogger(__name__)

def require_permission(permission_code: str):
    async def dependency(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        allowed = await role_has_permission(
            db=db,
            role_id=current_user.role_id,
            permission_code=permission_code,
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ErrorMessage.INSUFFICIENT_PERMISSION,
            )

        return current_user

    return dependency