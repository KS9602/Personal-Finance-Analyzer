from fastapi import FastAPI

from app.auth.auth_endpoint import auth_router
from app.api.v1.router import api_router
from app.api.healthcheck import healthcheck_router
from app.exceptions.exception_utils import register_exception_handlers
from app.core.middlewear import CustomCORSMiddleware
from app.core.lifespan_utils import lifespan

def create_app() -> FastAPI:

    app = FastAPI(title="PFA", lifespan=lifespan)

    register_exception_handlers(app)

    app.include_router(auth_router)
    app.include_router(api_router)
    app.include_router(healthcheck_router)

    app.add_middleware(CustomCORSMiddleware)

    return app

app = create_app()