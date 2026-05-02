from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import get_settings
from app.models.schemas import ContentItem, ContentWrite
from app.services.audit_service import write_audit
from app.services.auth_service import optional_admin, require_admin
from app.services.content_service import ContentError, MarkdownStore


def make_content_router(section: str, tag: str) -> APIRouter:
    router = APIRouter(prefix=f"/{section}", tags=[tag])

    def store() -> MarkdownStore:
        return MarkdownStore(get_settings().data_path, section)

    @router.get("", response_model=list[ContentItem])
    def list_items(include_drafts: bool = Query(False), actor: str | None = Depends(optional_admin)):
        if include_drafts and not actor:
            raise HTTPException(status_code=401, detail="admin token required")
        return store().list(include_drafts=include_drafts)

    @router.get("/{slug}", response_model=ContentItem)
    def get_item(slug: str, include_drafts: bool = Query(False), actor: str | None = Depends(optional_admin)):
        if include_drafts and not actor:
            raise HTTPException(status_code=401, detail="admin token required")
        try:
            item = store().read(slug)
            if item.meta.draft and not include_drafts:
                raise FileNotFoundError(slug)
            return item
        except ContentError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="content not found")

    @router.post("", response_model=ContentItem)
    def create_item(payload: ContentWrite, actor: str = Depends(require_admin)):
        try:
            current = store()
            if current.exists(payload.slug):
                write_audit(actor=actor, action=f"{section}.create", resource=section, target=payload.slug, result="failed", message="Slug already exists")
                raise HTTPException(status_code=409, detail="slug already exists")
            item = current.save(payload)
            write_audit(actor=actor, action=f"{section}.create", resource=section, target=item.slug, result="success", message="Content created", detail={"draft": item.meta.draft})
            return item
        except HTTPException:
            raise
        except ContentError as exc:
            write_audit(actor=actor, action=f"{section}.create", resource=section, target=payload.slug, result="failed", message=str(exc))
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.put("/{slug}", response_model=ContentItem)
    def update_item(slug: str, payload: ContentWrite, actor: str = Depends(require_admin)):
        try:
            before = store().read(slug)
            item = store().save(payload, old_slug=slug)
            action = f"{section}.publish" if before.meta.draft and not item.meta.draft else f"{section}.update"
            if not before.meta.draft and item.meta.draft:
                action = f"{section}.unpublish"
            write_audit(actor=actor, action=action, resource=section, target=item.slug, result="success", message="Content updated", detail={"oldSlug": slug, "draft": item.meta.draft})
            return item
        except ContentError as exc:
            status_code = 409 if "already exists" in str(exc) else 400
            write_audit(actor=actor, action=f"{section}.update", resource=section, target=slug, result="failed", message=str(exc))
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc
        except FileNotFoundError:
            write_audit(actor=actor, action=f"{section}.update", resource=section, target=slug, result="failed", message="content not found")
            raise HTTPException(status_code=404, detail="content not found")

    @router.delete("/{slug}")
    def delete_item(slug: str, actor: str = Depends(require_admin)):
        try:
            store().delete(slug)
            write_audit(actor=actor, action=f"{section}.delete", resource=section, target=slug, result="success", message="Content deleted")
            return {"ok": True}
        except ContentError as exc:
            write_audit(actor=actor, action=f"{section}.delete", resource=section, target=slug, result="failed", message=str(exc))
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except FileNotFoundError:
            write_audit(actor=actor, action=f"{section}.delete", resource=section, target=slug, result="failed", message="content not found")
            raise HTTPException(status_code=404, detail="content not found")

    return router
