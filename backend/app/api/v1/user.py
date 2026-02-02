from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user_crud import read_all_user
from models import db_helper
from schemas.user import UserRead
from utils.secure import get_current_user

router = APIRouter()


@router.get("/list")
async def list_all_user(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    return await read_all_user(session)


@router.get("/me")
async def user_information(
    current_user: Annotated[UserRead, Depends(get_current_user)],
):
    return current_user
