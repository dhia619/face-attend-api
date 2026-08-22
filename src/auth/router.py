from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_current_user
from src.auth.schemas import *
import src.auth.service as service 
from src.users.schemas import UserRead
from src.users.models import User

auth_router = APIRouter()


@auth_router.post("/login", response_model=TokenResponse)
async def login(
    login_request: LoginRequest,
    session: AsyncSession = Depends(get_db)
):
    return await service.authenticate_user(
        db=session,
        email=login_request.email,
        password=login_request.password
    )


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_db)
):
    return await service.refresh_token(session, payload.refresh_token)


@auth_router.get("/me", response_model=UserRead)
async def me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await service.logout(session, current_user)