from fastapi import Depends, Cookie
from fastapi.responses import RedirectResponse
import httpx
import logging
import uuid
from urllib.parse import urlencode

from app.core.dependencies import get_users_service, get_redis_service
from app.exceptions.exceptions import AuthorizationException
from app.core.config import settings
from app.auth.utils_auth import (
    save_session,
    public,
    anonymous_only,
    authenticated,
    get_sub,
    generate_code_verifier,
    generate_code_challenge
)
from app.core.redis_service import RedisService
from app.auth.auth_api_route import AuthApiRouter



log = logging.getLogger(__name__)

auth_router = AuthApiRouter(prefix="/auth")


@auth_router.get("/me")
@public
async def me(session_id: str = Cookie(None)):
    return {"authenticated": bool(session_id)}


@auth_router.get("/login", response_class=RedirectResponse)
@anonymous_only
async def login(redis: RedisService = Depends(get_redis_service)):

    state = str(uuid.uuid4())
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    await redis.save_state_code_verifier_redis(state,code_verifier)

    params = {
        "client_id": settings.PFA_BACKEND_CLIENT_ID,
        "redirect_uri": settings.PFA_BACKEND_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }

    auth_url = f"{settings.KEYCLOAK_URL}/realms/{settings.REALM}/protocol/openid-connect/auth?{urlencode(params)}"

    return RedirectResponse(auth_url, status_code=302)


@auth_router.get("/callback", response_class=RedirectResponse)
@anonymous_only
async def callback(
        state: str,
        code: str,
        users_service  = Depends(get_users_service),
        redis: RedisService = Depends(get_redis_service)
):
    log.debug(f"CALBACK {state}")

    code_verifier = await redis.get_code_verifier_by_state_redis(state)
    log.debug(f"code_verifiercode_verifier {code_verifier}")
    if not code_verifier:
        raise AuthorizationException(status_code=400, detail="Missing PKCE")


    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.PFA_BACKEND_CLIENT_ID,
        "client_secret": settings.PFA_BACKEND_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.PFA_BACKEND_REDIRECT_URI,
        "code_verifier": code_verifier
    }
    log.debug(f"Keycloak payload {payload}")

    async with httpx.AsyncClient() as client:
        result = await client.post(
            settings.TOKEN_URL,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    log.debug(f"Keycloak result {result}")
    log.debug(f"Keycloak result {result.text}")

    result.raise_for_status()
    
    log.debug(f"Keycloak result {result.json()}")
    sub = get_sub(result.json().get("access_token"))
    if not sub:
        raise AuthorizationException(status_code=401, detail="Missing sub")
    user = await users_service.get_if_exist_or_create(sub)
    session_id = await save_session(redis,result.json())

    response = RedirectResponse(url=settings.PFA_FRONTEND_REDIRECT_URI)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60
    )
    response.delete_cookie("code")
    return response


@auth_router.get("/logout", response_class=RedirectResponse)
@public
async def logout(
        session_id: str = Cookie(...),
        redis: RedisService = Depends(get_redis_service)
):

    token_data = await redis.get_tokens_by_session_redis(session_id)
    if not token_data:
        log.info("Invalid session_id")
        response = RedirectResponse(settings.PFA_FRONTEND_REDIRECT_URI)
        response.delete_cookie("session_id")
        return response
    id_token = token_data.get("id_token")
    response = RedirectResponse(settings.build_logout_url(id_token))
    await redis.delete_tokens_redis(session_id)
    return response


@auth_router.get("/logout/callback",response_class=RedirectResponse)
@public
async def logout_callback():
    response = RedirectResponse(settings.PFA_FRONTEND_REDIRECT_URI)
    response.delete_cookie("session_id")
    return response

