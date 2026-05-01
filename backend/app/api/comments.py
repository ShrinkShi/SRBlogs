from fastapi import APIRouter, HTTPException
from datetime import datetime
from uuid import uuid4
import bleach
from app.config import get_settings
from app.models.schemas import CommentCreate, CommentItem
from app.services.json_service import JsonStore

router = APIRouter(prefix="/comments", tags=["comments"])
ALLOWED_RESOURCES = {"posts", "moments", "chatters"}


def _store(resource: str, slug: str) -> JsonStore:
    if resource not in ALLOWED_RESOURCES:
        raise HTTPException(status_code=400, detail="非法评论资源")
    safe_slug = "".join(ch for ch in slug if ch.isalnum() or ch in "-_")
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
