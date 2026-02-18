from fastapi import FastAPI

from app.auth.auth_endpoint import auth_router
from app.api.v1.router import api_router
from app.api.healthcheck import healthcheck_router
from app.auth.middlewear import CheckAuthMiddlewar
from app.utils.redis_base import init_redis,close_redis





def create_app() -> FastAPI:
    app = FastAPI(title="PFA")
    @app.on_event("startup")
    async def on_startup():
        await init_redis()

    @app.on_event("shutdown")
    async def on_shutdown():
        await close_redis()

    app.include_router(auth_router)
    app.include_router(api_router)
    app.include_router(healthcheck_router)

    app.add_middleware(CheckAuthMiddlewar)

    return app

app = create_app()