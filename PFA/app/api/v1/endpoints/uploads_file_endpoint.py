from fastapi import APIRouter, UploadFile, File
import shutil
from pathlib import Path

router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"]
)

UPLOAD_DIR = Path("uploads")    # TODO WYWALIC DO CONFIG
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "status": "saved"}