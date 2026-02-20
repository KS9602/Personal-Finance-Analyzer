from fastapi import Response, Depends, Cookie, Request
from fastapi.responses import RedirectResponse
import httpx
import logging
import uuid
import os
import hashlib
import base64
from urllib.parse import urlencode
import jwt


from app.services.users_service import UsersService
from app.utils.dependencies import get_users_service
from app.exceptions.exceptions import AuthorizationException
from app.auth.schemas import LoginData
from app.config import settings
from app.auth.utils_auth import (
    save_session,
    public,
    anonymous_only,
    authenticated,
    AuthApiRouter,
    get_sub,
    generate_code_verifier,
    generate_code_challenge
)
from app.utils.redis_utils import (
    save_state_code_verifier_redis,
    get_code_verifier_by_state_redis,
    get_tokens_by_session_redis,
    delete_tokens_redis
)


log = logging.getLogger(__name__)

auth_router = AuthApiRouter(prefix="/auth")


@auth_router.get("/me")
@authenticated
async def me(session_id: str = Cookie(...)):
    return {"authenticated": bool(session_id)}


@auth_router.get("/login", response_class=RedirectResponse)
@anonymous_only
async def login(response: Response):

    state = str(uuid.uuid4())
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    await save_state_code_verifier_redis(state,code_verifier)

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
        users_service  = Depends(get_users_service)
):
    log.debug(f"CALBACK {state}")

    code_verifier = await get_code_verifier_by_state_redis(state)
    log.debug(f"code_verifiercode_verifier {code_verifier}")
    if not code_verifier:
        raise AuthorizationException(status_code=400, detail="Missing PKCE")


    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.PFA_BACKEND_CLIENT_ID,
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
    result.raise_for_status()
    
    log.debug(f"Keycloak result {result.json()}")
    sub = get_sub(result.json().get("access_token"))
    if not sub:
        raise AuthorizationException(status_code=401, detail="Missing sub")
    user = await users_service.get_if_exist_or_create(sub)
    session_id = await save_session(result.json())

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
@authenticated
async def logout(session_id: str = Cookie(...)):
    token_data = await get_tokens_by_session_redis(session_id)
    if not token_data:
        log.info("Invalid session_id")
        raise AuthorizationException(status_code=400, detail="Invalid session_id")
    id_token = token_data.get("id_token")
    response = RedirectResponse(settings.build_logout_url(id_token))
    await delete_tokens_redis(session_id)
    return response


@auth_router.get("/logout/callback",response_class=RedirectResponse)
@public
async def logout_callback():
    response = RedirectResponse(settings.PFA_FRONTEND_REDIRECT_URI)
    response.delete_cookie("session_id")
    return response

