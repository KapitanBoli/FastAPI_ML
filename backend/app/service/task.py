from redis.asyncio import Redis
from uuid_extensions import uuid7
import json
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from models import Video

QUEUE_NAME = "video_tasks"


async def create_task(session: AsyncSession, redis: Redis, video_path: Path) -> str:
    task_id = str(uuid7())
    task = Video(id=task_id, status="processing")
    session.add(task)
    await session.commit()

    await redis.set(f"task:{task_id}:status", "processing")

    payload = {
        "task_id": task_id,
        "video_path": str(video_path),
    }

    await redis.rpush(QUEUE_NAME, json.dumps(payload))
    return task_id


async def get_task_result(session: AsyncSession, task_id: str) -> dict:
    task = await session.get(Video, task_id)
    if not task:
        return {"status": "not_found"}
    return {"status": task.status, "result": task.result}
