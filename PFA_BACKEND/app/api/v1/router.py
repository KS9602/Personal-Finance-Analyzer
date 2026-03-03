from fastapi import APIRouter

from .endpoints import dashboard_endpoints

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(dashboard_endpoints.router)