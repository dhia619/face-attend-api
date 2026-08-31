from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.users.models import User
from src.users.schemas import UserUpdate
from src.shared.pagination import get_page_offset

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)

async def insert_user(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user

async def delete_user(
    db:AsyncSession,
    user_id: int
) -> bool:

    result = await db.execute(delete(User).where(User.id == user_id))
    return result.rowcount == 1

async def update_user(
    db: AsyncSession,
    user: User,
    user_data: UserUpdate,
) -> User:

    data = user_data.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(user, field, value)

    await db.flush()

    return user

async def get_users(
    db: AsyncSession,
    page: int,
    page_size: int,
    limit: int | None = None
) -> list[User]:

    result = await db.execute(
        select(User).
        order_by(User.id).
        offset(get_page_offset(page, page_size)).
        limit(limit if limit is not None else page_size)
    )
    return list(result.scalars().all())