from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from jose import ExpiredSignatureError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from crud.user_crud import create_user, login_user, get_user
from models import db_helper
from models.db_helper import get_redis_client
from schemas.token import TokenType, RefreshToken
from schemas.user import UserCreate
from utils.secure import (
    create_access_token,
    create_refresh_token,
    oauth2_scheme,
    decode_token,
    decode_token_without_expiry,
)
from utils.token import add_token_to_redis, delete_tokens, get_valid_token

router = APIRouter()


@router.post("/register")
async def create_users(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user_data: UserCreate,
):
    user = await create_user(session, user_data)
    if user is None:
        raise HTTPException(
            status_code=400, detail="The user with this email already exists"
        )
    return user


@router.post("/login")
async def login_users(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    redis: Redis = Depends(get_redis_client),
):
    user = await login_user(session, user_data)
    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    await add_token_to_redis(
        redis,
        user,
        access_token,
        TokenType.ACCESS,
        settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    await add_token_to_redis(
        redis,
        user,
        refresh_token,
        TokenType.REFRESH,
        settings.auth.REFRESH_TOKEN_EXPIRE_MINUTES,
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/new_access_token")
async def get_new_access_token(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    token: RefreshToken,
    redis: Redis = Depends(get_redis_client),
):

    try:
        payload = decode_token(token.refresh_token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=403,
            detail="Your token has expired. Please log in again.",
        )

    if payload["type"] == "refresh":
        user_id = payload["sub"]
        valid_refresh_tokens = await get_valid_token(redis, user_id, TokenType.REFRESH)
        if valid_refresh_tokens and token.refresh_token not in valid_refresh_tokens:
            raise HTTPException(status_code=403, detail="Refresh token invalid")
        user = await get_user(user_id, session)

        access_token = create_access_token(user.id)

        await delete_tokens(redis, user, TokenType.ACCESS)

        await add_token_to_redis(
            redis,
            user,
            access_token,
            TokenType.ACCESS,
            settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
    else:
        raise HTTPException(status_code=404, detail="Incorrect token")


@router.post("/logout")
async def logout_user(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis_client),
):
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
    try:
        payload = decode_token(token)
        user_id = payload["sub"]

        user = await get_user(user_id, session)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await delete_tokens(redis, user, TokenType.ACCESS)
        await delete_tokens(redis, user, TokenType.REFRESH)

        return {
            "message": "Successfully logged out",
            "user_id": str(user_id),
        }
    except ExpiredSignatureError:
        try:
            payload = decode_token_without_expiry(token)
            user_id = payload.get("sub")
            if user_id:
                user = await get_user(user_id, session)
                if user:
                    await delete_tokens(redis, user, TokenType.ACCESS)
                    await delete_tokens(redis, user, TokenType.REFRESH)
        except:
            pass

        raise HTTPException(
            status_code=401, detail="Token expired, but logged out successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
