from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi import status

from src.auth.security import (
    verify_secret, 
    create_access_token, 
    create_refresh_token,
    decode_refresh_token
)

from src.auth.constants import ErrorMessage
from src.users.repository import get_user_by_email, get_user_by_id

async def authenticate_user(
    db: AsyncSession, 
    email: str, 
    password: str
) -> dict[str, str]:
    
    user = await get_user_by_email(db, email)
    if not user or not verify_secret(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=ErrorMessage.INVALID_CREDENTIALS
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

async def refresh_token(
    db: AsyncSession, 
    refresh_token: str
) -> dict[str, str]:
    
    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessage.INVALID_CREDENTIALS
        )

    user_id = payload.get("sub")
    user = await get_user_by_id(db, int(user_id))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.USER_NOT_FOUND
        )

    return {
        "access_token": create_access_token({"sub": str(user.id)}),
        "refresh_token": create_refresh_token({"sub": str(user.id)}),
        "token_type": "bearer"
    }