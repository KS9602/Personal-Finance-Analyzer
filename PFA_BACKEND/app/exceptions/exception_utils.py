from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from app.exceptions.exceptions import AuthorizationException
from app.config import settings

def register_exception_handlers(app: FastAPI):
    async def authorization_handler(request: Request, exc: AuthorizationException):
        if exc.status_code == 401:
            return RedirectResponse(f"{settings.PFA_FRONTEND_REDIRECT_URI}/auth/login")

        return RedirectResponse(f"{settings.PFA_FRONTEND_REDIRECT_URI}/error")


    app.add_exception_handler(AuthorizationException, authorization_handler)


# TODO pododawac reszte kategorii
