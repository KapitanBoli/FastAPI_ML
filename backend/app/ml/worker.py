import json
import asyncio

from ml.processor import process_video
from models import Video
from models.db_helper import db_helper
from redis.asyncio import Redis
import redis.asyncio as aioredis
from config import settings

QUEUE_NAME = "video_tasks"


async def worker_loop():
    print("ML worker started")

    redis: Redis = await aioredis.from_url(
        url=str(settings.redis.url),
        db=settings.redis.db,
        decode_responses=True,
    )

    try:
        while True:
            _, payload = await redis.blpop(QUEUE_NAME)
            data = json.loads(payload)

            task_id = data["task_id"]
            video_path = data["video_path"]

            result = process_video(video_path)

            async with db_helper.session_factory() as session:
                task = await session.get(Video, task_id)
                task.status = "done"
                task.result = result
                await session.commit()

            # await redis.set(f"task:{task_id}:status", "done", ex=60)
            await redis.delete(f"task:{task_id}:status")
    finally:
        await redis.close()
        await db_helper.dispose()


if __name__ == "__main__":
    asyncio.run(worker_loop())
