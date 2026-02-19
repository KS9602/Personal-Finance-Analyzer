import json
import uuid
from typing import Optional, Dict

import app.utils.redis_base as r
from app.config import settings


async def save_simple_key_value(key: str, value: str, exp: int) -> None:
    await r.redis_client.setex(key, exp, value)

async def get_simple_value(key: str) -> str:
    return await r.redis_client.get(key)

async def delete_by_value(key: str) -> None:
    return await r.redis_client.delete(key)

async def save_session_redis(session_id: str, tokens_with_id: Dict) -> None:
    await save_simple_key_value(session_id, json.dumps(tokens_with_id), settings.REDIS_EXPIRE_SEC)

async def get_tokens_by_session_redis(session_id: str) -> Dict[str, str] | None:
    tokens = await get_simple_value(session_id)
    if tokens: return json.loads(tokens)
    else: return None

async def save_state_code_verifier_redis(state: str, code_verifier: str) -> None:
    await save_simple_key_value(state, code_verifier, settings.CODE_VERIFIER_EXP)
    
async def get_code_verifier_by_state_redis(state: str) -> str:
    return await get_simple_value(state)

async def delete_tokens_redis(session_id: str) -> None:
    await delete_by_value(session_id)