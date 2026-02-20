import json
from typing import Dict
from redis.asyncio import Redis

import app.core.redis_base as r
from app.core.config import settings


class RedisService:
    def __init__(self, redis: Redis):
        self.redis = redis


    async def save_simple_key_value(self, key: str, value: str, exp: int) -> None:
        await self.redis.setex(key, exp, value)

    async def get_simple_value(self, key: str) -> str:
        return await self.redis.get(key)

    async def delete_by_value(self, key: str) -> None:
        return await self.redis.delete(key)

    async def save_session_redis(self, session_id: str, tokens_with_id: Dict) -> None:
        await self.save_simple_key_value(session_id, json.dumps(tokens_with_id), settings.REDIS_EXPIRE_SEC)

    async def get_tokens_by_session_redis(self, session_id: str) -> Dict[str, str] | None:
        tokens = await self.get_simple_value(session_id)
        if tokens: return json.loads(tokens)
        else: return None

    async def save_state_code_verifier_redis(self, state: str, code_verifier: str) -> None:
        await self.save_simple_key_value(state, code_verifier, settings.CODE_VERIFIER_EXP)

    async def get_code_verifier_by_state_redis(self, state: str) -> str:
        return await self.get_simple_value(state)

    async def delete_tokens_redis(self, session_id: str) -> None:
        await self.delete_by_value(session_id)