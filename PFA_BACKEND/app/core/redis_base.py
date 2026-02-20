from redis.asyncio import Redis, ConnectionPool
import logging

from app.core.config import settings

log = logging.getLogger(__name__)

# https://oneuptime.com/blog/post/2026-01-21-redis-fastapi-integration/view         kradzione z
class RedisClient:
    def __init__(self):
        self.pool: ConnectionPool = None
        self.client: Redis = None

    async def connect(self):
        self.pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=50,
            decode_responses=True
        )
        log.info("Redis UP")
        self.client = Redis(connection_pool=self.pool)

    async def disconnect(self):
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()
        log.info("Redis DWON")

    def get_client(self) -> Redis:
        return self.client

redis_client = RedisClient()



