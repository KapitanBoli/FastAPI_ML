from typing import Sequence, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from schemas.user import UserCreate, UserAuth
from utils.secure import get_password_hash, verify_password


async def create_user(session: AsyncSession, user_data: UserCreate) -> User | None:
    user_data = user_data.model_dump()
    user_data["password"] = get_password_hash(user_data["password"])
    stmt = select(User).where(User.email == user_data["email"])
    result = await session.scalar(stmt)
    if result:
        return None
    user = User(**user_data)
    session.add(user)
    await session.commit()
    return user


async def read_all_user(session: AsyncSession) -> Sequence[User]:
    stmt = select(User)
    result = await session.scalars(stmt)
    return result.all()


async def get_user(user_id: int, session: AsyncSession) -> User:
    stmt = select(User).where(User.id == user_id)
    result = await session.scalar(stmt)
    return result


async def login_user(session: AsyncSession, user_data: UserAuth) -> User | None:
    stmt = select(User).where(User.email == user_data.username)
    user = await session.scalar(stmt)

    if (
        not user
        or verify_password(user_data.password, cast(str, user.password)) is False
    ):
        return None
    return user
