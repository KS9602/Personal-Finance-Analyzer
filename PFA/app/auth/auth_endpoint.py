from fastapi import APIRouter, Response
import requests
import uuid
from typing import Dict, Any

from app.auth.schemas import LoginData
from app.utils.redis_utils import save_session_redis
from app.config import settings
from app.auth.utils_auth import save_session, public, AuthApiRouter


auth_router = AuthApiRouter(prefix="/auth")



@auth_router.post("/login")
@public
async def login(login_data: LoginData, response: Response):
    token_url = f"{settings.KEYCLOAK_URL}/realms/{settings.REALM}/protocol/openid-connect/token"

    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.CLIENT_ID,
        "code": login_data.code,
        "redirect_uri": settings.REDIRECT_URI,
        "code_verifier": login_data.code_verifier
    }
    # result = await requests.post(url=token_url, payload=payload)
    # result.raise_for_status()
    # session_id = save_session(result.json())
    result = {
        "access_token":"123",
        "refresh_token":"321"
    }
    session_id = await save_session(result)

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax"
    )
    return {"message": "Logged in"}

