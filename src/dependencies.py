from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.repository import get_user_by_id
from src.config import get_settings
from src.auth.security import decode_access_token
from src.auth.constants import ErrorMessage

settings = get_settings()

user_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.BASE_API_PATH}/auth/login",
    scheme_name="UserAuth"
)

async def get_current_user(
    token: str = Depends(user_oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=ErrorMessage.INVALID_TOKEN
        )
    user_id = payload.get("sub")
    user = await get_user_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=ErrorMessage.USER_NOT_FOUND
        )
    return user