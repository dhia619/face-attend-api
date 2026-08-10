from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import LoginRequest, TokenResponse
from src.auth.service import authenticate_user
from src.database import get_db

auth_router = APIRouter()

@auth_router.post("/login", response_model=TokenResponse)
async def login(
    login_request: LoginRequest,
    session: AsyncSession = Depends(get_db)
):
    return await authenticate_user(
        db=session,
        email=login_request.email,
        password=login_request.password
    )