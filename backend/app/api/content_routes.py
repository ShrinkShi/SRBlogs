from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import get_settings
from app.models.schemas import ContentItem, ContentWrite
from app.services.auth_service import require_admin
from app.services.content_service import ContentError, MarkdownStore


def make_content_router(section: str, tag: str) -> APIRouter:
    router = APIRouter(prefix=f"/{section}", tags=[tag])

    def store() -> MarkdownStore:
        return MarkdownStore(get_settings().data_path, section)

    @router.get("", response_model=list[ContentItem])
    def list_items(include_drafts: bool = Query(False)):
        return store().list(include_drafts=include_drafts)

    @router.get("/{slug}", response_model=ContentItem)
    def get_item(slug: str):
        try:
            return store().read(slug)
        except ContentError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="content not found")

    @router.post("", response_model=ContentItem, dependencies=[Depends(require_admin)])
    def create_item(payload: ContentWrite):
        try:
            current = store()
            if current.exists(payload.slug):
                raise HTTPException(status_code=409, detail="slug already exists")
            return current.save(payload)
        except HTTPException:
            raise
        except ContentError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.put("/{slug}", response_model=ContentItem, dependencies=[Depends(require_admin)])
    def update_item(slug: str, payload: ContentWrite):
        try:
            return store().save(payload, old_slug=slug)
        except ContentError as exc:
            status_code = 409 if "already exists" in str(exc) else 400
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    @router.delete("/{slug}", dependencies=[Depends(require_admin)])
    def delete_item(slug: str):
        try:
            store().delete(slug)
            return {"ok": True}
        except ContentError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="content not found")

    return router
