from fastapi import APIRouter, Depends

from app.models.schemas import JsonWrite
from app.services.auth_service import require_admin
from app.services.file_store import resolve_data_path, safe_read_text, safe_write_text

router = APIRouter(prefix="/about", tags=["about"])


@router.get("")
def get_about():
    file = resolve_data_path("about.md")
    if not file.exists():
        safe_write_text(file, "# About\n\nWrite your introduction here.\n", make_backup=False)
    return {"content": safe_read_text(file)}


@router.put("", dependencies=[Depends(require_admin)])
def update_about(payload: JsonWrite):
    file = resolve_data_path("about.md")
    content = str(payload.data.get("content", "")) if isinstance(payload.data, dict) else str(payload.data)
    safe_write_text(file, content)
    return {"ok": True}
