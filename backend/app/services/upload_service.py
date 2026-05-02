from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import get_settings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}


class UploadTypeError(ValueError):
    pass


class UploadTooLargeError(ValueError):
    pass


async def save_upload(file: UploadFile) -> dict:
    settings = get_settings()
    ext = Path(file.filename or "").suffix.lower()
    allowed_mime_types = {item.strip() for item in settings.upload_allowed_types.split(",") if item.strip()}
    if ext not in ALLOWED_EXTENSIONS:
        raise UploadTypeError("Only jpg/jpeg/png/gif/webp/svg images are allowed.")
    if file.content_type not in allowed_mime_types:
        raise UploadTypeError("Unsupported image MIME type.")

    content = await file.read()
    if len(content) > settings.upload_max_size:
        raise UploadTooLargeError("Image file is too large.")

    if settings.upload_driver == "oss":
        raise NotImplementedError("OSS upload is reserved for a server-side SDK integration.")

    upload_dir = settings.data_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    name = f"{uuid4().hex}{ext}"
    target = upload_dir / name
    target.write_bytes(content)
    return {
        "filename": name,
        "url": f"{settings.public_base_url.rstrip('/')}/uploads/{name}",
        "size": len(content),
    }
