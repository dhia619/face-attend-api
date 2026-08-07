from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi import status

from src.auth.security import verify_password, create_access_token, create_refresh_token
from src.auth.constants import ErrorMessage
from src.user.repository import get_user_by_email

async def authenticate_user(db: AsyncSession, email: str, password: str) -> dict[str, str] | None:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessage.INVALID_CREDENTIALS)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }