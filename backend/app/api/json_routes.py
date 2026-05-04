from fastapi import APIRouter, Depends, HTTPException
from app.config import get_settings
from app.models.schemas import JsonWrite
from app.services.audit_service import write_audit
from app.services.auth_service import require_admin
from app.services.json_service import JsonStore

DEFAULTS = {
    "friends.json": [],
    "projects.json": [],
    "music.json": [],
    "photos/photos.json": [],
    "settings.json": {},
}


def make_json_router(prefix: str, filename: str, tag: str) -> APIRouter:
    router = APIRouter(prefix=f"/{prefix}", tags=[tag])

    def store() -> JsonStore:
        return JsonStore(get_settings().data_path, filename, DEFAULTS.get(filename, []))

    @router.get("")
    def read_json():
        data = store().read()
        if prefix == "music" and isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    try:
                        item["likes"] = max(0, int(item.get("likes") or 0))
                    except (TypeError, ValueError):
                        item["likes"] = 0
        return data

    @router.put("")
    def write_json(payload: JsonWrite, actor: str = Depends(require_admin)):
        current = store().read()
        action = f"{prefix}.update"
        if isinstance(current, list) and isinstance(payload.data, list):
            if len(payload.data) > len(current):
                action = f"{prefix}.create"
            elif len(payload.data) < len(current):
                action = f"{prefix}.delete"
        try:
            result = store().write(payload.data)
            write_audit(
                actor=actor,
                action=action,
                resource=prefix,
                target=filename,
                result="success",
                message=f"{prefix} data saved",
                detail={"count": len(payload.data) if isinstance(payload.data, list) else None},
            )
            return result
        except Exception as exc:
            write_audit(actor=actor, action=action, resource=prefix, target=filename, result="failed", message=str(exc))
            raise

    if prefix == "music":
        def song_key(item: dict) -> str:
            return str(item.get("id") or item.get("title") or item.get("url") or "").strip()

        @router.post("/{song_id}/likes")
        def update_music_likes(song_id: str, payload: JsonWrite):
            data = store().read()
            if not isinstance(data, list):
                raise HTTPException(status_code=400, detail={"code": "INVALID_MUSIC_DATA", "message": "音乐数据格式不正确", "detail": {}})
            liked = bool((payload.data or {}).get("liked")) if isinstance(payload.data, dict) else False
            for item in data:
                if not isinstance(item, dict):
                    continue
                if song_key(item) != song_id:
                    continue
                try:
                    current = max(0, int(item.get("likes") or 0))
                except (TypeError, ValueError):
                    current = 0
                item["likes"] = max(0, current + (1 if liked else -1))
                store().write(data)
                return {"id": song_key(item), "likes": item["likes"], "liked": liked}
            raise HTTPException(status_code=404, detail={"code": "MUSIC_NOT_FOUND", "message": "歌曲不存在", "detail": {"id": song_id}})

    return router
