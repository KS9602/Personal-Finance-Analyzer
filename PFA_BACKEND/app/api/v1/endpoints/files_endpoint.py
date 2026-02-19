from fastapi import APIRouter

import app.api.v1.endpoints.uploads_file_endpoint as upload

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)

router.include_router(upload.router)