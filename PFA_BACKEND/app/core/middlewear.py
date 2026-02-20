from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response


from app.core.config import settings

class CustomCORSMiddleware(CORSMiddleware):
    def __init__(self, app):
        super().__init__(
            app=app,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


class CheckAuthMiddlewar(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # wywalone do custom api routa

        # endpoint = request.scope.get("endpoint")
        # print("QQQQQQQQQQQ")
        # print("QQQQQQQQQQQ")
        # print(request.scope)
        # print(getattr(endpoint,"public"))
        # print("QQQQQQQQQQQ")
        # if endpoint:
        #     if getattr(endpoint,"public") == True:
        #         return await call_next(request)
        #
        # request_session_id = request.cookies.get("session_id")
        # if request_session_id is None:
        #     raise HTTPException(status_code=404, detail="Session not found in cookie")
        # tokens = get_session_redis(session_id=request_session_id)
        # if tokens is None:
        #     raise HTTPException(status_code=404, detail="Session not found in redis")
        #
        # # request.state.user = "JAN"       #
        # request.state.access_token = tokens.get("access_token")
        # request.state.refrest_token = tokens.get("refresh_token")
        return await call_next(request)


class CheckAccessToken(BaseHTTPMiddleware):
    pass

