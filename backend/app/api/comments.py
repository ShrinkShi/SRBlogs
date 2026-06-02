from datetime import datetime
from pathlib import Path
from uuid import uuid4

import bleach
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.config import get_settings
from app.api.auth import read_visitor_user
from app.models.schemas import CommentCreate, CommentIndexItem, CommentItem
from app.services.audit_service import write_audit
from app.services.auth_service import require_admin, security
from app.services.content_service import MarkdownStore
from app.services.file_store import FileStoreError, resolve_data_path, safe_read_json, validate_slug
from app.services.json_service import JsonStore
from app.services.upload_service import UploadTooLargeError, UploadTypeError, save_comment_upload

router = APIRouter(prefix="/comments", tags=["comments"])
admin_router = APIRouter(prefix="/admin/comments", tags=["comments"], dependencies=[Depends(require_admin)])
ALLOWED_RESOURCES = {"posts", "moments", "chatters", "music", "photos"}


def _store(resource: str, slug: str) -> JsonStore:
    if resource not in ALLOWED_RESOURCES:
        raise HTTPException(status_code=400, detail="留言资源类型无效。")
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


def _comment_options() -> dict:
    data = JsonStore(get_settings().data_path, "settings.json", {}).read()
    comments = data.get("comments") if isinstance(data, dict) else {}
    return comments if isinstance(comments, dict) else {}


def _comments_enabled(options: dict) -> bool:
    return options.get("enabled", True) is not False


def _max_comment_length(options: dict) -> int:
    try:
        value = int(options.get("maxLength", 1000))
    except (TypeError, ValueError):
        value = 1000
    return max(1, min(value, 5000))


def _mask_email(email: str) -> str:
    if not email or "@" not in email:
        return ""
    name, domain = email.split("@", 1)
    if len(name) <= 2:
        masked_name = name[:1] + "*"
    else:
        masked_name = name[:1] + "***" + name[-1:]
    return f"{masked_name}@{domain}"


def _public_comment(comment: dict, options: dict) -> dict:
    item = dict(comment)
    email = str(item.get("email") or "")
    item["email"] = _mask_email(email) if options.get("showEmail") is True else ""
    item.setdefault("parentId", "")
    item.setdefault("replyTo", {})
    item.setdefault("attachments", [])
    return item


def _admin_avatar() -> str:
    data = JsonStore(get_settings().data_path, "settings.json", {}).read()
    if not isinstance(data, dict):
        return ""
    candidates = [
        data.get("avatar"),
        data.get("avatarUrl"),
        data.get("adminAvatar"),
        data.get("authorAvatar"),
    ]
    for value in candidates:
        if value:
            return bleach.clean(str(value), tags=[], strip=True)
    return ""


def _comment_identity(request: Request, admin_actor: str | None) -> dict:
    if admin_actor:
        return {
            "provider": "admin",
            "id": admin_actor,
            "name": "管理员",
            "avatar": _admin_avatar(),
        }
    visitor_user = read_visitor_user(request)
    if not visitor_user or not visitor_user.get("id"):
        raise HTTPException(status_code=401, detail="请先登录后再留言。")
    return visitor_user


def _read_admin_or_none(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> str | None:
    if credentials is None:
        return None
    settings = get_settings()
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
    except JWTError:
        return None
    sub = payload.get("sub")
    return sub if sub == settings.admin_username else None


def _reply_snapshot(comments: list[dict], parent_id: str) -> dict[str, str]:
    if not parent_id:
        return {}
    for comment in comments:
        if str(comment.get("id") or "") == parent_id:
            content = bleach.clean(str(comment.get("content") or ""), tags=[], strip=True)
            return {
                "id": parent_id,
                "author": bleach.clean(str(comment.get("author") or "访客"), tags=[], strip=True),
                "content": content[:120],
            }
    raise HTTPException(status_code=404, detail="被回复的留言不存在。")


def _clean_attachments(attachments: list) -> list[dict]:
    result: list[dict] = []
    for attachment in attachments[:5]:
        item = attachment.model_dump() if hasattr(attachment, "model_dump") else dict(attachment)
        result.append({
            "url": bleach.clean(str(item.get("url") or ""), tags=[], strip=True),
            "filename": bleach.clean(str(item.get("filename") or ""), tags=[], strip=True),
            "originalName": bleach.clean(str(item.get("originalName") or ""), tags=[], strip=True),
            "size": int(item.get("size") or 0),
            "kind": bleach.clean(str(item.get("kind") or "file"), tags=[], strip=True),
        })
    return [item for item in result if item["url"]]


@router.get("/{resource}/{slug}", response_model=list[CommentItem])
def list_comments(resource: str, slug: str):
    options = _comment_options()
    return [_public_comment(item, options) for item in _store(resource, slug).read()]


@router.post("/upload")
async def upload_comment_file(
    request: Request,
    file: UploadFile = File(...),
    admin_actor: str | None = Depends(_read_admin_or_none),
):
    options = _comment_options()
    if not admin_actor and not _comments_enabled(options):
        raise HTTPException(status_code=403, detail="留言板暂未开放。")
    identity = _comment_identity(request, admin_actor)
    try:
        result = await save_comment_upload(file)
        write_audit(
            actor=str(identity.get("name") or identity.get("id") or "visitor"),
            action="comment.upload",
            resource="comments",
            target=result.get("filename", file.filename or ""),
            result="success",
            message="Comment attachment uploaded",
            detail={"size": result.get("size"), "kind": result.get("kind")},
        )
        return result
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except UploadTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except UploadTypeError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc


@router.post("/{resource}/{slug}", response_model=CommentItem)
def create_comment(
    resource: str,
    slug: str,
    payload: CommentCreate,
    request: Request,
    admin_actor: str | None = Depends(_read_admin_or_none),
):
    options = _comment_options()
    if not admin_actor and not _comments_enabled(options):
        raise HTTPException(status_code=403, detail="留言板暂未开放。")
    max_length = _max_comment_length(options)
    if len(payload.content.strip()) > max_length:
        raise HTTPException(status_code=400, detail=f"留言内容不能超过 {max_length} 个字符。")
    store = _store(resource, slug)
    comments = store.read()
    identity = _comment_identity(request, admin_actor)
    parent_id = bleach.clean(str(payload.parentId or ""), tags=[], strip=True)
    provider = bleach.clean(str(identity.get("provider") or ""), tags=[], strip=True)
    provider_id = bleach.clean(str(identity.get("id") or ""), tags=[], strip=True)
    author = bleach.clean(str(identity.get("name") or provider_id or "Visitor"), tags=[], strip=True)
    item = {
        "id": uuid4().hex,
        "author": author,
        "email": "",
        "avatar": bleach.clean(str(identity.get("avatar") or ""), tags=[], strip=True),
        "provider": provider,
        "providerId": provider_id,
        "githubLogin": provider_id if provider == "github" else "",
        "parentId": parent_id,
        "replyTo": _reply_snapshot(comments, parent_id),
        "attachments": _clean_attachments(payload.attachments),
        "content": bleach.clean(payload.content, tags=[], strip=True),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    comments.append(item)
    store.write(comments)
    write_audit(actor=item["author"], action="comment.create", resource=resource, target=slug, result="success", message="Comment created", detail={"commentId": item["id"]})
    return _public_comment(item, options)


@router.delete("/{resource}/{slug}/{comment_id}", dependencies=[Depends(require_admin)])
def delete_comment(resource: str, slug: str, comment_id: str, actor: str = Depends(require_admin)):
    store = _store(resource, slug)
    comments = store.read()
    next_comments = [item for item in comments if item.get("id") != comment_id]
    if len(next_comments) == len(comments):
        write_audit(actor=actor, action="comment.delete", resource=resource, target=slug, result="failed", message="comment not found", detail={"commentId": comment_id})
        raise HTTPException(status_code=404, detail="留言不存在。")
    store.write(next_comments)
    write_audit(actor=actor, action="comment.delete", resource=resource, target=slug, result="success", message="Comment deleted", detail={"commentId": comment_id})
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
