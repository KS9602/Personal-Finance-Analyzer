import json
import uuid
from typing import Optional, Dict

import app.utils.redis_base as r
from app.config import settings



async def save_session_redis(session_id: str, tokens: Dict):
    await r.redis_client.setex(session_id, settings.REDIS_EXPIRE_SEC, json.dumps(tokens))

async def get_session_redis(session_id: str) -> Dict[str, str] | None:
    tokens = await r.redis_client.get(session_id)
    if tokens: return json.loads(tokens)
    else: return None

