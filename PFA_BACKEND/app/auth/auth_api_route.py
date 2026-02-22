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
from app.auth.utils_auth import (
    save_session,
    decode_token,
    check_azp,
    check_iss,
    logout_kc_redirect,
    payload_refresh
)

log = logging.getLogger(__name__)

class AuthApiRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,route_class=AuthApiRoute, **kwargs)


class AuthApiRoute(APIRoute):

    def get_route_handler(self):
        original_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            redis = RedisService(request.app.state.redis)
            endpoint = self.endpoint
            auth_mode = getattr(endpoint, "auth_mode")
            session_id = request.cookies.get("session_id")
            tokens = None

            log.debug("AUTHROUTE")
            log.debug(f"endpoint: {endpoint}")
            log.debug(f"auth_mode: {auth_mode}")
            log.debug(f"sesion_id: {session_id}")

            if not auth_mode:
                log.debug("No auth_mode, redirecting to home")
                return RedirectResponse(settings.PFA_FRONTEND_REDIRECT_URI)

            if session_id:
                log.debug("session_id exists, fetching tokens ")
                tokens = await redis.get_tokens_by_session_redis(session_id)
                log.debug(f"tokens: {tokens}")

                if not tokens:
                    log.debug("No tokens found, redirect to home")
                    response = RedirectResponse(
                        url=settings.PFA_FRONTEND_REDIRECT_URI,
                        status_code=302
                    )
                    response.delete_cookie("session_id")
                    return response
            else:
                log.debug("No session_id in cookie")

            if auth_mode == "public":
                log.debug("auth_moe PUBLIC")
                return await original_handler(request)

            if auth_mode == "anonymous_only":
                log.debug("auth_moe ANONYMOUS_ONLY")

                if tokens or session_id:
                    log.debug("User has session_id/tokens, redirecting")
                    return RedirectResponse(settings.PFA_FRONTEND_REDIRECT_URI)

                log.debug("User is anonymous, continue request")
                return await original_handler(request)

            if auth_mode == "authenticated":
                log.debug("auth_moe AUTHENTICATED")


                if not tokens or not session_id:
                    log.debug("Missing tokens,session_id, return 401")
                    raise AuthorizationException(status_code=401)

            # TODO Ogarnac certy

                access_token = tokens.get("access_token")
                refresh_token = tokens.get("refresh_token")
                id_token = tokens.get("id_token")

                result = await self.manage_auth(access_token, refresh_token, id_token, session_id, redis)
                if isinstance(result, RedirectResponse):
                    return result

                request.state.sub = result
                return await original_handler(request)

            raise AuthorizationException(401, detail="how did you get here")

        return custom_route_handler


    async def manage_auth(
            self,
            access_token,
            refresh_token,
            id_token,
            session_id,
            redis
    ):
        access_exp, access_azp, access_iss, access_sub = decode_token(access_token)
        refresh_exp, refresh_azp, refresh_iss, refresh_sub = decode_token(refresh_token)
        check_azp(access_azp, refresh_azp)
        check_iss(access_iss, refresh_iss)

        now = int(time.time())

        log.debug("Start manage exp tokens")
        if access_exp > now:
            log.debug("Access token is ok")
            return access_sub


        log.debug("Access token is expired, checking refresh")
        if refresh_exp < now:
            log.debug("Refresh token is expired, redirect to logout")
            await redis.delete_tokens_redis(session_id)
            return logout_kc_redirect(id_token)
        else:
            log.debug("Refresh token is ok, trying get new tokens")
            payload = payload_refresh(refresh_token)
            log.debug(f"Keycloak payload for refresh {payload}")

            async with httpx.AsyncClient() as client:
                result = await client.post(
                    settings.TOKEN_URL,
                    data=payload,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

            log.debug(f"Exchange tokens result.text: {result.text}")
            try:
                result.raise_for_status()
            except httpx.HTTPStatusError:
                await redis.delete_tokens_redis(session_id)
                return logout_kc_redirect(id_token)
            new_tokens = result.json()
            await save_session(redis, new_tokens, session_id)
            log.debug("Gets new tokens")
            _, _, _, new_sub = decode_token(new_tokens.get("access_token"))
            return new_sub

