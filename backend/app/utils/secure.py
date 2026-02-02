from datetime import datetime, timedelta, timezone
from typing import Any, Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from redis import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings

from jose import jwt, ExpiredSignatureError

from models import User
from models.db_helper import get_redis_client, db_helper
from schemas.token import TokenType
from utils.token import get_valid_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str | Any):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"exp": expire, "sub": str(subject), "type": "access"}
    return jwt.encode(
        payload, settings.auth.secret_key, algorithm=settings.auth.ALGORITHM
    )


def create_refresh_token(subject: str | Any):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.auth.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    payload = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(
        payload, settings.auth.secret_key, algorithm=settings.auth.ALGORITHM
    )

def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token=token,
        key=settings.auth.secret_key,
        algorithms=settings.auth.ALGORITHM,
    )

def decode_token_without_expiry(token: str) -> dict[str, Any]:
    return jwt.decode(
        token=token,
        key=settings.auth.secret_key,
        algorithms=settings.auth.ALGORITHM,
        options={"verify_exp" : False}
    )


async def get_current_user(
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
        access_token: str = Depends(oauth2_scheme),
        redis_client: Redis = Depends(get_redis_client)
) -> User:
    try:
        payload = decode_token(access_token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=403,
            detail="Your token has expired. Please log in again.",
        )
    user_id = payload["sub"]
    valid_access_tokens = await get_valid_token(
        redis_client, user_id, TokenType.ACCESS
    )

    if valid_access_tokens and access_token not in valid_access_tokens:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )

    if not valid_access_tokens:
        raise HTTPException(
            status_code=401,
            detail="Token has been revoked"
        )

    stmt = select(User).where(User.id == user_id)
    user = await session.scalar(stmt)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user