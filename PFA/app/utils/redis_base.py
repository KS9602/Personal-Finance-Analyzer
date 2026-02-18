import redis.asyncio as ra
from typing import Optional

from app.config import settings

redis_client: Optional[ra.Redis] = None

async def init_redis() -> ra.Redis:
    global redis_client
    if redis_client is None:
        redis_client = await ra.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        await redis_client.ping()


async def close_redis() -> None:
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None