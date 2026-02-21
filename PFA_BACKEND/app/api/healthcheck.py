from app.auth.auth_api_route import AuthApiRouter
from app.auth.utils_auth import public

healthcheck_router = AuthApiRouter(prefix="/healthcheck")

@healthcheck_router.get("/")
async def healthcheck():
    return {"status":"ok"}