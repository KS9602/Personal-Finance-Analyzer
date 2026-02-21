from fastapi import APIRouter

from .endpoints import example_entpoint, frontend_endpoint, files_endpoint, dashboard_endpoints

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(example_entpoint.router)
api_router.include_router(frontend_endpoint.router)
api_router.include_router(files_endpoint.router)
api_router.include_router(dashboard_endpoints.router)