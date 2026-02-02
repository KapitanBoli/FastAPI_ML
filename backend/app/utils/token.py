from datetime import timedelta

from pydantic import UUID7
from redis.asyncio import Redis

from models import User
from schemas.token import TokenType

async def add_token_to_redis(redis_client: Redis, user: User, token: str, token_type: TokenType, expire_time: int | None = None):
    token_key = f"user:{user.id}:{token_type.value}"
    valid_token = await get_valid_token(redis_client, user.id, token_type)
    await redis_client.sadd(token_key,token)
    if not valid_token:
        await redis_client.expire(token_key, timedelta(minutes=expire_time))

async def get_valid_token(redis_client: Redis, user_id: UUID7, token_type: TokenType):
    token_key = f"user:{user_id}:{token_type.value}"
    valid_tokens = await redis_client.smembers(token_key)
    return valid_tokens

async def delete_tokens(redis_client: Redis, user: User, token_type: TokenType):
    token_key = f"user:{user.id}:{token_type.value}"
    valid_tokens = await redis_client.exists(token_key)
    if valid_tokens is not None:
        await redis_client.delete(token_key)

