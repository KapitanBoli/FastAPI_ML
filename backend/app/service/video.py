from pathlib import Path
from fastapi import UploadFile, HTTPException
from uuid_extensions import uuid7

from config import settings


async def upload_video(file: UploadFile) -> dict:
    if file.content_type not in settings.video.allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")

    ext = Path(file.filename).suffix
    filename = f"{uuid7()}{ext}"
    file_path = settings.video.upload_dir / filename

    size = 0
    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.video.max_size:
                buffer.close()
                file_path.unlink(missing_ok=True)
                raise HTTPException(status_code=400, detail="The file is too big")
            buffer.write(chunk)

    return {
        "filename": filename,
        "content_type": file.content_type,
        "size_mb": round(size / 1024 / 1024, 2),
        "message": "Video uploaded successfully",
    }
