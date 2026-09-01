import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


def save_upload_file(upload_file: UploadFile) -> Path:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    destino = upload_dir / f"{uuid.uuid4()}_{upload_file.filename}"
    with destino.open("wb") as buffer:
        buffer.write(upload_file.file.read())

    return destino
