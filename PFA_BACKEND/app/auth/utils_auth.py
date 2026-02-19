import uuid
from typing import Dict, Any
from fastapi.routing import APIRoute
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import jwt
import os
import base64
import hashlib

from app.config import settings
from app.utils.redis_utils import get_tokens_by_session_redis, save_session_redis
from app.exceptions.exceptions import AuthorizationException

import logging

log = logging.getLogger(__name__)


class AuthApiRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,route_class=AuthApiRoute, **kwargs)


class AuthApiRoute(APIRoute):

    def get_route_handler(self):
        original_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            endpoint = self.endpoint
            auth_mode = getattr(endpoint, "auth_mode")
            session_id = request.cookies.get("session_id")
            tokens = None

            if not auth_mode:
                return RedirectResponse(settings.PFA_FRONTEND_REDIRECT_URI)
            if session_id:
                tokens = await get_tokens_by_session_redis(session_id)
            if auth_mode == "public":
                return await original_handler(request)
            if auth_mode == "anonymous_only":
                if tokens:
                    return RedirectResponse(settings.PFA_FRONTEND_REDIRECT_URI)
                return await original_handler(request)

            if not tokens:
                raise AuthorizationException(status_code=401)

            request.state.user = "JAN"
            return await original_handler(request)


        return custom_route_handler

async def save_session(result: Dict[str, Any]) -> int:
    log.info("Zapisuje tokeny")
    session_id = str(uuid.uuid4())
    tokens_with_id = {
        "id_token": result.get("id_token"),
        "access_token": result.get("access_token"),
        "refresh_token": result.get("refresh_token")
    }
    await save_session_redis(session_id,tokens_with_id)

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
