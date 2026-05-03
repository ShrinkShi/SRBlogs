from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import get_settings

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".svg",
    ".mp3",
    ".wav",
    ".ogg",
    ".m4a",
    ".mp4",
    ".webm",
    ".mov",
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}
IMAGE_MAX_SIZE = 10 * 1024 * 1024
AUDIO_MAX_SIZE = 100 * 1024 * 1024
VIDEO_MAX_SIZE = 200 * 1024 * 1024


class UploadTypeError(ValueError):
    pass


class UploadTooLargeError(ValueError):
    pass


def _kind_and_limit(ext: str, content_type: str | None) -> tuple[str, int]:
    if ext in IMAGE_EXTENSIONS or (content_type or "").startswith("image/"):
        return "image", IMAGE_MAX_SIZE
    if ext in AUDIO_EXTENSIONS or (content_type or "").startswith("audio/"):
        return "audio", AUDIO_MAX_SIZE
    if ext in VIDEO_EXTENSIONS or (content_type or "").startswith("video/"):
        return "video", VIDEO_MAX_SIZE
    return "file", get_settings().upload_max_size


async def save_upload(file: UploadFile) -> dict:
    settings = get_settings()
    ext = Path(file.filename or "").suffix.lower()
    allowed_mime_types = {item.strip() for item in settings.upload_allowed_types.split(",") if item.strip()}
    if ext not in ALLOWED_EXTENSIONS:
        raise UploadTypeError("Only configured image/audio/video file types are allowed.")
    if file.content_type not in allowed_mime_types:
        raise UploadTypeError("Unsupported file MIME type.")

    kind, max_size = _kind_and_limit(ext, file.content_type)
    content = await file.read()
    if len(content) > max_size:
        label = {"image": "Image", "audio": "Audio", "video": "Video"}.get(kind, "Uploaded file")
        raise UploadTooLargeError(f"{label} exceeds the {max_size // 1024 // 1024} MB upload limit.")

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
