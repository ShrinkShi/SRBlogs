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
    ".mp3",
    ".wav",
    ".ogg",
    ".m4a",
    ".mp4",
    ".webm",
    ".mov",
    ".lrc",
    ".txt",
}
COMMENT_UPLOAD_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".txt", ".md", ".pdf"}
COMMENT_UPLOAD_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "text/plain",
    "text/markdown",
    "application/pdf",
    "application/octet-stream",
}
COMMENT_UPLOAD_MAX_SIZE = 2 * 1024 * 1024

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}
LYRIC_EXTENSIONS = {".lrc", ".txt"}
IMAGE_MAX_SIZE = 10 * 1024 * 1024
AUDIO_MAX_SIZE = 100 * 1024 * 1024
VIDEO_MAX_SIZE = 200 * 1024 * 1024
LYRIC_MAX_SIZE = 1 * 1024 * 1024


class UploadTypeError(ValueError):
    pass


class UploadTooLargeError(ValueError):
    pass


def _kind_and_limit(ext: str, content_type: str | None) -> tuple[str, int]:
    if ext in LYRIC_EXTENSIONS:
        return "lyric", LYRIC_MAX_SIZE
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
        raise UploadTypeError("Only configured image/audio/video/lyric file types are allowed.")
    is_lyric = ext in LYRIC_EXTENSIONS
    if not is_lyric and file.content_type not in allowed_mime_types:
        raise UploadTypeError("Unsupported file MIME type.")
    if is_lyric and file.content_type not in {"text/plain", "application/octet-stream", "application/x-subrip"}:
        raise UploadTypeError("Only .lrc or .txt lyric files are allowed.")

    kind, max_size = _kind_and_limit(ext, file.content_type)
    content = await file.read()
    if len(content) > max_size:
        label = {"image": "Image", "audio": "Audio", "video": "Video", "lyric": "Lyric"}.get(kind, "Uploaded file")
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


async def save_comment_upload(file: UploadFile) -> dict:
    settings = get_settings()
    ext = Path(file.filename or "").suffix.lower()
    if ext not in COMMENT_UPLOAD_EXTENSIONS:
        raise UploadTypeError("Comment uploads only allow images, .txt, .md, and .pdf files.")
    if file.content_type not in COMMENT_UPLOAD_MIME_TYPES and not (file.content_type or "").startswith("image/"):
        raise UploadTypeError("Unsupported comment upload MIME type.")
    content = await file.read()
    if len(content) > COMMENT_UPLOAD_MAX_SIZE:
        raise UploadTooLargeError("Comment upload exceeds the 2 MB upload limit.")
    if settings.upload_driver == "oss":
        raise NotImplementedError("OSS upload is reserved for a server-side SDK integration.")
    upload_dir = settings.data_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    name = f"{uuid4().hex}{ext}"
    target = upload_dir / name
    target.write_bytes(content)
    kind = "image" if ext in IMAGE_EXTENSIONS or (file.content_type or "").startswith("image/") else "file"
    return {
        "filename": name,
        "originalName": file.filename or name,
        "url": f"{settings.public_base_url.rstrip('/')}/uploads/{name}",
        "size": len(content),
        "kind": kind,
    }
