import uuid
from typing import Dict, Any
import logging
import jwt
import os
import base64
import hashlib

from app.core.redis_service import RedisService


log = logging.getLogger(__name__)




async def save_session(redis : RedisService, result: Dict[str, Any], session_id: str = None ) -> int:
    log.info("Zapisuje tokeny")
    if not session_id:
        session_id = str(uuid.uuid4())
    tokens_with_id = {
        "id_token": result.get("id_token"),
        "access_token": result.get("access_token"),
        "refresh_token": result.get("refresh_token")
    }
    await redis.save_session_redis(session_id,tokens_with_id)

    return session_id

def get_sub(token: str) -> str | None:      # TODO podmienic na ten z weryfikacja certow
    payload = jwt.decode(
        token,
        options={"verify_signature": False}
    )

    sub = payload["sub"]
    if sub: return sub

def public(fn):
    fn.auth_mode  = "public"
    return fn

def anonymous_only(fn):
    fn.auth_mode  = "anonymous_only"
    return fn

def authenticated(fn):
    fn.auth_mode  = "authenticated"
    return fn

def generate_code_verifier():
    random_bytes = os.urandom(32)
    return base64.urlsafe_b64encode(random_bytes).rstrip(b"=").decode("utf-8")

def generate_code_challenge(verifier: str):
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("utf-8")
