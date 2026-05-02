from fastapi import APIRouter, Depends
from app.config import get_settings
from app.services.auth_service import require_admin
from app.services.file_store import safe_read_json

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", dependencies=[Depends(require_admin)])
def stats():
    base = get_settings().data_path
    photos = safe_read_json(base / "photos" / "photos.json", [])
    return {
        "posts": len(list((base / "posts").glob("*.md"))),
        "moments": len(list((base / "moments").glob("*.md"))),
        "chatters": len(list((base / "chatters").glob("*.md"))),
        "photos": len(photos) if isinstance(photos, list) else 0,
    }
