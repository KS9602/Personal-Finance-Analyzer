import time

import httpx
from fastapi.routing import APIRoute, APIRouter
from fastapi import Request
from fastapi.responses import RedirectResponse
import jwt
import logging

from app.core.redis_service import RedisService
from app.exceptions.exceptions import AuthorizationException
from app.core.config import settings
from app.auth.utils_auth import save_session

log = logging.getLogger(__name__)

class AuthApiRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,route_class=AuthApiRoute, **kwargs)


class AuthApiRoute(APIRoute):

    def get_route_handler(self):
        original_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            # redis = get_redis_service(request.app.state.redis)
            redis = RedisService(request.app.state.redis)
            endpoint = self.endpoint
            auth_mode = getattr(endpoint, "auth_mode")
            session_id = request.cookies.get("session_id")
            tokens = None

            if not auth_mode:
                return RedirectResponse(settings.PFA_FRONTEND_REDIRECT_URI)
            if session_id:
                tokens = await redis.get_tokens_by_session_redis(session_id)
            if auth_mode == "public":
                return await original_handler(request)
            if auth_mode == "anonymous_only":
                if tokens:
                    return RedirectResponse(settings.PFA_FRONTEND_REDIRECT_URI)
                return await original_handler(request)

            if not tokens or not tokens.get("access_token") or not tokens.get("refresh_token"):
                raise AuthorizationException(status_code=401)

            # TODO
            # TODO  Ogarnac certy
            # TODO

            # TODO
            # TODO
            # TODO Rozdzielic na mniejsze funkcji
            # TODO
            # TODO

            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")
            id_token = tokens.get("id_token")

            payload_access_token = jwt.decode(
                access_token,
                options={"verify_signature": False}
            )
            now = int(time.time())
            exp_access = payload_access_token.get("exp", 0)

            if exp_access < now:
                payload_refresh_token = jwt.decode(
                    refresh_token,
                    options={"verify_signature": False}
                )
                exp_refresh = payload_refresh_token.get("exp")

                if exp_refresh < now:
                    await redis.delete_tokens_redis(session_id)
                    redirect = RedirectResponse(
                        url=settings.build_logout_url(id_token),
                        status_code=302
                    )
                    redirect.delete_cookie("session_id")
                    return redirect
                else:
                    payload = {
                        "grant_type": "refresh_token",
                        "client_id": settings.PFA_BACKEND_CLIENT_ID,
                        "refresh_token": refresh_token,
                        # "client_secret": settings.PFA_BACKEND_CLIENT_SECRET
                    }
                    log.debug(f"Keycloak payload for refresh {payload}")

                    async with httpx.AsyncClient() as client:
                        result = await client.post(
                            settings.TOKEN_URL,
                            data=payload,
                            headers={"Content-Type": "application/x-www-form-urlencoded"},
                        )
                    result.raise_for_status()
                    await save_session(redis, result.json(), session_id)
                    return await original_handler(request)

            if payload_access_token and payload_access_token.get("sub"):
                request.state.sub = payload_access_token.get("sub")

            return await original_handler(request)

        return custom_route_handler

