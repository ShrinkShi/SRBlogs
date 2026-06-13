import re

from fastapi import APIRouter, Depends, HTTPException, Request
from app.api.auth import read_visitor_user
from app.config import get_settings
from app.models.schemas import JsonWrite
from app.services.audit_service import write_audit
from app.services.auth_service import optional_admin, require_admin
from app.services.file_store import FileStoreError, validate_slug
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

    def safe_like_slug(value: str) -> str:
        try:
            return validate_slug(value)
        except FileStoreError:
            raise HTTPException(status_code=400, detail="Invalid slug") from None

    def likes_store(slug: str) -> JsonStore:
        return JsonStore(get_settings().data_path, f"likes/{prefix}-{safe_like_slug(slug)}.json", {"users": []})

    def like_users(slug: str) -> set[str]:
        data = likes_store(slug).read()
        users = data.get("users", []) if isinstance(data, dict) else []
        return {str(item) for item in users if str(item).strip()}

    def write_like_users(slug: str, users: set[str]) -> int:
        next_users = sorted(users)
        likes_store(slug).write({"users": next_users})
        return len(next_users)

    def like_identity(request: Request, actor: str | None) -> str | None:
        if actor:
            return f"admin:{actor}"
        visitor = read_visitor_user(request)
        if not visitor or not visitor.get("id"):
            return None
        return f"{visitor.get('provider') or 'visitor'}:{visitor.get('id')}"

    def json_slug(value: str, fallback: str) -> str:
        slug = re.sub(r"[^a-z0-9_-]+", "-", str(value or "").lower().strip()).strip("-")
        return slug or fallback

    def photo_album_slug(item: dict, index: int) -> str:
        photos = item.get("photos") if isinstance(item.get("photos"), list) else []
        if photos:
            return json_slug(item.get("title") or item.get("cover") or f"album-{index + 1}", f"album-{index + 1}")
        return json_slug(item.get("title") or item.get("url") or f"album-{index + 1}", f"album-{index + 1}")

    def find_photo_album(data: list, slug: str) -> tuple[int, dict]:
        safe_slug = safe_like_slug(slug)
        for index, item in enumerate(data):
            if isinstance(item, dict) and photo_album_slug(item, index) == safe_slug:
                return index, item
        raise HTTPException(status_code=404, detail={"code": "PHOTO_ALBUM_NOT_FOUND", "message": "相册不存在", "detail": {"slug": slug}})

    def sync_json_like_count(slug: str, count: int) -> None:
        if prefix != "photos":
            return
        data = store().read()
        if not isinstance(data, list):
            return
        index, item = find_photo_album(data, slug)
        if int(item.get("like_count") or 0) == count:
            return
        item["like_count"] = count
        data[index] = item
        store().write(data)

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

    if prefix == "photos":
        @router.get("/{slug}/likes")
        def get_photo_like_status(slug: str, request: Request, actor: str | None = Depends(optional_admin)):
            data = store().read()
            if not isinstance(data, list):
                raise HTTPException(status_code=400, detail={"code": "INVALID_PHOTO_DATA", "message": "相册数据格式不正确", "detail": {}})
            find_photo_album(data, slug)
            users = like_users(slug)
            identity = like_identity(request, actor)
            count = len(users)
            sync_json_like_count(slug, count)
            return {"liked": bool(identity and identity in users), "like_count": count}

        @router.post("/{slug}/likes")
        def toggle_photo_like(slug: str, request: Request, actor: str | None = Depends(optional_admin)):
            data = store().read()
            if not isinstance(data, list):
                raise HTTPException(status_code=400, detail={"code": "INVALID_PHOTO_DATA", "message": "相册数据格式不正确", "detail": {}})
            find_photo_album(data, slug)
            identity = like_identity(request, actor)
            if not identity:
                raise HTTPException(status_code=401, detail="请先登录后再点赞。")
            users = like_users(slug)
            liked = identity not in users
            if liked:
                users.add(identity)
            else:
                users.discard(identity)
            count = write_like_users(slug, users)
            sync_json_like_count(slug, count)
            write_audit(actor=identity, action="photos.like", resource="photos", target=slug, result="success", message="Photo album like toggled", detail={"liked": liked, "like_count": count})
            return {"liked": liked, "like_count": count}

    return router
