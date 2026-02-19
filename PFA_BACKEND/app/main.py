from app.config import settings
from fastapi import FastAPI

from app.auth.auth_endpoint import auth_router
from app.api.v1.router import api_router
from app.api.healthcheck import healthcheck_router
from app.auth.middlewear import CheckAuthMiddlewar
from fastapi.middleware.cors import CORSMiddleware
from app.utils.redis_base import init_redis,close_redis
from app.utils.logger import setup_logging
from app.exceptions.exception_utils import register_exception_handlers
from app.db.connection import close_engine

import logging


def create_app() -> FastAPI:
    app = FastAPI(title="PFA")
    @app.on_event("startup")
    async def on_startup():
        await init_redis()
        setup_logging()

    @app.on_event("shutdown")
    async def on_shutdown():
        await close_redis()
        await close_engine()


    register_exception_handlers(app)

    app.include_router(auth_router)
    app.include_router(api_router)
    app.include_router(healthcheck_router)

    app.add_middleware(         # todo zrobic oddzielna klase?
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(CheckAuthMiddlewar)

    return app

app = create_app()