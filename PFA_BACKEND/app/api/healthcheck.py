from app.auth.utils_auth import AuthApiRouter
from app.auth.utils_auth import public

healthcheck_router = AuthApiRouter(prefix="/healthcheck")

@healthcheck_router.get("/")
async def healthcheck():
    return {"status":"ok"}