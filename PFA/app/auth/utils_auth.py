import uuid
from typing import Dict, Any
from fastapi.routing import APIRoute
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from app.utils.redis_utils import save_session_redis
from app.config import settings
from app.utils.redis_utils import get_session_redis



class AuthApiRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,route_class=AuthApiRoute, **kwargs)
        

class AuthApiRoute(APIRoute):

    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            endpoint = self.endpoint
            if endpoint:
                if getattr(endpoint,"public", False):
                    print("PUBLIC")
                    return await original_route_handler(request)
            print("PRIWATE")
            request_session_id = request.cookies.get("session_id")
            if request_session_id is None:
                raise HTTPException(status_code=404, detail="Session not found in cookie")
            tokens = get_session_redis(session_id=request_session_id)
            if tokens is None:
                raise HTTPException(status_code=404, detail="Session not found in redis")

            # request.state.user = "JAN"       #
            request.state.access_token = tokens.get("access_token")
            request.state.refrest_token = tokens.get("refresh_token")

            return await original_route_handler(request)

        return custom_route_handler

async def save_session(result: Dict[str, Any]) -> int:
    session_id = str(uuid.uuid4())
    tokens = {
        "access_token": result.get("access_token"),
        "refrest_token": result.get("refrest_token")
    }
    await save_session_redis(session_id,tokens)
    print(f"zapisnno {session_id} dla {tokens}")
    return session_id

def public(fn):
    fn.public = True
    return fn