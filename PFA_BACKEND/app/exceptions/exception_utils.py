from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse

from app.exceptions.exceptions import AuthorizationException
from app.core.config import settings

def register_exception_handlers(app: FastAPI):
    async def authorization_handler(request: Request, exc: AuthorizationException):

        if "application/json" in request.headers.get("accept", ""):
            return JSONResponse(
                status_code=401,
                content={"authenticated": False}
            )

        if exc.status_code == 401:
            return RedirectResponse(f"{settings.PFA_FRONTEND_REDIRECT_URI}/auth/login")

        return RedirectResponse(f"{settings.PFA_FRONTEND_REDIRECT_URI}/error")


    app.add_exception_handler(AuthorizationException, authorization_handler)


# TODO pododawac reszte kategorii
