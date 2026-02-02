from typing import Annotated

from fastapi import APIRouter, UploadFile, File, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models import db_helper
from models.db_helper import get_redis_client
from service.task import create_task, get_task_result
from service.video import upload_video

router = APIRouter()


@router.post("/upload")
async def upload_and_process(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    redis: Redis = Depends(get_redis_client),
    file: UploadFile = File(...),
):
    video_info = await upload_video(file)
    video_path = settings.video.upload_dir / video_info["filename"]
    task_id = await create_task(session, redis, video_path)
    return {"task_id": task_id, "status": "processing"}


@router.get("/result/{task_id}")
async def get_result(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    task_id: str,
):
    return await get_task_result(session, task_id)
