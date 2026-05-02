from datetime import datetime
from pathlib import Path
from uuid import uuid4

import bleach
from fastapi import APIRouter, Depends, HTTPException

from app.config import get_settings
from app.models.schemas import CommentCreate, CommentIndexItem, CommentItem
from app.services.auth_service import require_admin
from app.services.content_service import MarkdownStore
from app.services.file_store import FileStoreError, resolve_data_path, safe_read_json, validate_slug
from app.services.json_service import JsonStore

router = APIRouter(prefix="/comments", tags=["comments"])
admin_router = APIRouter(prefix="/admin/comments", tags=["comments"], dependencies=[Depends(require_admin)])
ALLOWED_RESOURCES = {"posts", "moments", "chatters"}


def _store(resource: str, slug: str) -> JsonStore:
    if resource not in ALLOWED_RESOURCES:
        raise HTTPException(status_code=400, detail="Invalid comment resource")
    try:
        safe_slug = validate_slug(slug)
    except FileStoreError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return JsonStore(get_settings().data_path, f"comments/{resource}-{safe_slug}.json", [])


def _comment_title(resource: str, slug: str) -> str:
    try:
        return MarkdownStore(get_settings().data_path, resource).read(slug).meta.title
    except Exception:
        return slug


def _comment_file_to_key(file: Path) -> tuple[str, str] | None:
    if file.parent.name == ".backups" or file.suffix != ".json":
        return None
    stem = file.stem
    resource, sep, slug = stem.partition("-")
    if not sep or resource not in ALLOWED_RESOURCES:
        return None
    try:
        return resource, validate_slug(slug)
    except FileStoreError:
        return None


@router.get("/{resource}/{slug}", response_model=list[CommentItem])
def list_comments(resource: str, slug: str):
    return _store(resource, slug).read()


@router.post("/{resource}/{slug}", response_model=CommentItem)
def create_comment(resource: str, slug: str, payload: CommentCreate):
    store = _store(resource, slug)
    comments = store.read()
    item = {
        "id": uuid4().hex,
        "author": bleach.clean(payload.author, tags=[], strip=True),
        "email": bleach.clean(payload.email or "", tags=[], strip=True),
        "content": bleach.clean(payload.content, tags=[], strip=True),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    comments.append(item)
    store.write(comments)
    return item


@router.delete("/{resource}/{slug}/{comment_id}", dependencies=[Depends(require_admin)])
def delete_comment(resource: str, slug: str, comment_id: str):
    store = _store(resource, slug)
    comments = store.read()
    next_comments = [item for item in comments if item.get("id") != comment_id]
    if len(next_comments) == len(comments):
        raise HTTPException(status_code=404, detail="comment not found")
    store.write(next_comments)
    return {"ok": True}


@admin_router.get("/index", response_model=list[CommentIndexItem])
def comments_index():
    comments_dir = resolve_data_path("comments")
    if not comments_dir.exists():
        return []

    items: list[CommentIndexItem] = []
    for file in sorted(comments_dir.glob("*.json")):
        key = _comment_file_to_key(file)
        if not key:
            continue
        resource, slug = key
        comments = safe_read_json(file, [])
        if not isinstance(comments, list) or not comments:
            continue

        updated_at = ""
        for comment in comments:
            if isinstance(comment, dict):
                created_at = str(comment.get("created_at") or "")
                if created_at > updated_at:
                    updated_at = created_at
        if not updated_at:
            updated_at = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")

        items.append(CommentIndexItem(
            resource=resource,
            slug=slug,
            count=len(comments),
            updatedAt=updated_at,
            title=_comment_title(resource, slug),
        ))

    items.sort(key=lambda item: item.updatedAt or "", reverse=True)
    return items
