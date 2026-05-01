from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
from app.config import get_settings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}


async def save_upload(file: UploadFile) -> dict:
    settings = get_settings()
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("仅支持 jpg/jpeg/png/gif/webp/svg 图片")

    if settings.upload_driver == "oss":
        # 生产环境可在此处接入阿里云 OSS SDK：oss2.Auth + Bucket.put_object。
        # 当前保留配置位，避免把 AccessKey 写进前端或仓库。
        raise NotImplementedError("OSS 上传接口已预留，请在 upload_service.py 中接入 oss2")

    upload_dir = settings.data_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    name = f"{uuid4().hex}{ext}"
    target = upload_dir / name
    content = await file.read()
    target.write_bytes(content)
    return {
        "filename": name,
        "url": f"{settings.public_base_url.rstrip('/')}/uploads/{name}",
        "size": len(content),
    }
