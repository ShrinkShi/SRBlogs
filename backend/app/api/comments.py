from datetime import datetime
from uuid import uuid4

import bleach
from fastapi import APIRouter, Depends, HTTPException

from app.config import get_settings
from app.models.schemas import CommentCreate, CommentItem
from app.services.auth_service import require_admin
from app.services.file_store import FileStoreError, validate_slug
from app.services.json_service import JsonStore

router = APIRouter(prefix="/comments", tags=["comments"])
ALLOWED_RESOURCES = {"posts", "moments", "chatters"}


def _store(resource: str, slug: str) -> JsonStore:
    if resource not in ALLOWED_RESOURCES:
        raise HTTPException(status_code=400, detail="Invalid comment resource")
    try:
        safe_slug = validate_slug(slug)
    except FileStoreError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return JsonStore(get_settings().data_path, f"comments/{resource}-{safe_slug}.json", [])


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
