from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from src.auth.security import decode_access_token
from src.database import get_db
from src.users.repository import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(401, "Invalid or expired token")
    user_id = payload.get("sub")
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(401, "User not found")
    return user