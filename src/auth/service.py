from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi import status

import logging

from src.auth.security import (
    verify_secret, 
    hash_refresh_token,
    verify_refresh_token,
    create_access_token, 
    create_refresh_token,
    decode_refresh_token
)
from src.auth.constants import ErrorMessage
from src.users.repository import get_user_by_email, get_user_by_id, update_user
from src.users.schemas import UserUpdate
from src.users.models import User

logger = logging.getLogger(__name__)

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
    refresh_token = await _create_refresh_token(db, user)

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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessage.USER_NOT_FOUND
        )

    if not verify_refresh_token(refresh_token, user.refresh_token_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessage.INVALID_TOKEN
        )

    new_refresh_token = await _create_refresh_token(db, user)
    
    return {
        "access_token": create_access_token({"sub": str(user.id)}),
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

async def _create_refresh_token(
    db: AsyncSession,
    user: User,
) -> str:

    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    user.refresh_token_hash = hash_refresh_token(new_refresh_token)

    _ = await update_user(
        db=db,
        user=user,
        user_data=UserUpdate(
            refresh_token_hash=user.refresh_token_hash
        )
    )

    await db.commit()

    return new_refresh_token

async def logout(db: AsyncSession, user: User) -> None:
    user.refresh_token_hash = None
    await db.commit()
    logger.info(f"User {user.id} logged out")