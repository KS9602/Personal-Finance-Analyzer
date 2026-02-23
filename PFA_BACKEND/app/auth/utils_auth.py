import uuid
from typing import Dict, Any, TypeVar, Callable
import logging
import jwt
import os
import base64
import hashlib

from app.exceptions.exceptions import AuthorizationException
from fastapi.responses import RedirectResponse

from app.core.redis_service import RedisService
from app.core.config import settings


log = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable)


def check_azp(access_azp, refresh_azp) -> None:
    if access_azp != settings.PFA_BACKEND_CLIENT_ID or refresh_azp != settings.PFA_BACKEND_CLIENT_ID:
        log.debug("Invalid azp")
        raise AuthorizationException(status_code=401)

def check_iss(access_iss, refresh_iss) -> None:
    if access_iss != settings.ISS_URL or refresh_iss != settings.ISS_URL:
        raise AuthorizationException(status_code=401)

def payload_refresh(refresh_token) -> dict[str, str]:
    return {
    "grant_type": "refresh_token",
    "client_id": settings.PFA_BACKEND_CLIENT_ID,
    "refresh_token": refresh_token,
    "client_secret": settings.PFA_BACKEND_CLIENT_SECRET

}

def decode_token(token) -> tuple[int, str, str, str]:
    payload_access_token = jwt.decode(
        token,
        options={"verify_signature": False}
    )
    exp = payload_access_token.get("exp")
    azp = payload_access_token.get("azp")
    iss = payload_access_token.get("iss")
    sub = payload_access_token.get("sub")
    if None in (exp, azp, iss, sub):
        raise AuthorizationException()
    return exp, azp, iss, sub


def logout_redirect() -> None:
    response = RedirectResponse(
        url=settings.PFA_FRONTEND_REDIRECT_URI,
        status_code=302
    )
    response.delete_cookie("session_id")
    return response

def logout_kc_redirect(id_token) -> None:
    redirect = RedirectResponse(
        url=settings.build_logout_url(id_token),
        status_code=302
    )
    redirect.delete_cookie("session_id")

async def save_session(redis : RedisService, result: Dict[str, Any], session_id: str = None ) -> str:
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

def public(fn) -> F:
    fn.auth_mode  = "public"
    return fn

def anonymous_only(fn) -> F:
    fn.auth_mode  = "anonymous_only"
    return fn

def authenticated(fn) -> F:
    fn.auth_mode  = "authenticated"
    return fn

def generate_code_verifier() -> str:
    random_bytes = os.urandom(32)
    return base64.urlsafe_b64encode(random_bytes).rstrip(b"=").decode("utf-8")

def generate_code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("utf-8")
