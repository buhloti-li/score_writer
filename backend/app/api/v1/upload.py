import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}


@router.post("/images")
async def upload_images(
    files: list[UploadFile],
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 files per upload")

    uploaded = []
    for file in files:
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"File type {ext} not allowed")

        content = await file.read()
        if len(content) > settings.max_upload_size:
            raise HTTPException(status_code=400, detail="File too large (max 20MB)")

        file_id = uuid.uuid4()
        upload_dir = os.path.join(settings.local_storage_path, "uploads", str(user.id))
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, f"{file_id}{ext}")
        with open(file_path, "wb") as f:
            f.write(content)

        uploaded.append({
            "id": str(file_id),
            "filename": file.filename,
            "url": f"/storage/uploads/{user.id}/{file_id}{ext}",
            "size": len(content),
        })

    return {"files": uploaded}
