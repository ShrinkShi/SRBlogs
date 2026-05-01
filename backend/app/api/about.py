from fastapi import APIRouter, Depends
from app.config import get_settings
from app.models.schemas import JsonWrite
from app.services.auth_service import require_admin

router = APIRouter(prefix="/about", tags=["about"])


@router.get("")
def get_about():
    file = get_settings().data_path / "about.md"
    file.parent.mkdir(parents=True, exist_ok=True)
    if not file.exists():
        file.write_text("# 关于我\n\n这里写你的介绍。\n", encoding="utf-8")
    return {"content": file.read_text(encoding="utf-8")}


@router.put("", dependencies=[Depends(require_admin)])
def update_about(payload: JsonWrite):
    file = get_settings().data_path / "about.md"
    file.write_text(str(payload.data.get("content", "")) if isinstance(payload.data, dict) else str(payload.data), encoding="utf-8")
    return {"ok": True}
