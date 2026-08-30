from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.exceptions import HTTPException
from fastapi import status

from src.auth.security import hash_secret, verify_secret
from src.users.schemas import UserCreate, UserUpdate, ChangePassword
from src.users.constants import ErrorMessage as UserErrorMessage
from src.users.models import User
from src.users import repository
from src.employees.constants import ErrorMessage as EmployeeErrorMessage
from src.rbac.constants import RoleName

async def register_user(
    db: AsyncSession,
    user_data: UserCreate
) -> User:

    if await repository.get_user_by_email(db=db, email=user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=EmployeeErrorMessage.EMAIL_EXISTS
        )

    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        role_id=user_data.role_id,
        password_hash=hash_secret(user_data.password)
    )

    user = await repository.insert_user(db, user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=UserErrorMessage.CREATE_USER_ERROR
        )

    await db.commit()
    return user

async def get_user_by_id(
    db: AsyncSession, 
    user_id: int
) -> User:

    user = await repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=UserErrorMessage.USER_NOT_FOUND
        )
    return user  

async def get_users(
    db: AsyncSession
) -> list[User]:

    return await repository.get_users(db)

async def update_user(
    db: AsyncSession, 
    current_user: User,
    user_id: int,
    user_data: UserUpdate
) -> User:

    target_user = await get_user_by_id(db, user_id)
    if (target_user.role.name == RoleName.SUPER_ADMIN
        and current_user.role.name != RoleName.SUPER_ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=UserErrorMessage.CANNOT_EDIT_SUPER_ADMIN
        )

    updated_user = await repository.update_user(
        db=db, 
        user=target_user,
        user_data=user_data
    )

    await db.commit()
    await db.refresh(updated_user)

    return updated_user

async def delete_user(
    db: AsyncSession, 
    current_user: User,
    user_id: int
) -> bool:

    target_user = await get_user_by_id(db, user_id)

    if current_user.id == target_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=UserErrorMessage.CANNOT_DELETE_OWN_ACCOUNT
        )
    
    if (current_user.role.name != RoleName.SUPER_ADMIN
        and target_user.role.name == RoleName.SUPER_ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=UserErrorMessage.CANNOT_DELETE_SUPER_ADMIN
        )

    if await repository.delete_user(db, user_id):
        await db.commit()
        return True
    return False

async def change_password(
    db: AsyncSession,
    user_id: int,
    change_password_data: ChangePassword
) -> None:

    user = await get_user_by_id(db, user_id)

    if not verify_secret(change_password_data.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=UserErrorMessage.INCORRECT_PASSWORD
        )

    if not change_password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=UserErrorMessage.MISSING_PASSWORD
        )

    user.password_hash = hash_secret(change_password_data.new_password)

    await db.commit()