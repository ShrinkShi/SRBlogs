from fastapi import APIRouter, Depends, HTTPException, Query
from app.config import get_settings
from app.models.schemas import ContentItem, ContentWrite
from app.services.auth_service import require_admin
from app.services.content_service import MarkdownStore, ContentError


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
            item = store().read(slug)
            if item.meta.draft:
                # 公开端默认不展示草稿；后台编辑时列表可 include_drafts 后再按 slug 获取。
                return item
            return item
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="内容不存在")

    @router.post("", response_model=ContentItem, dependencies=[Depends(require_admin)])
    def create_item(payload: ContentWrite):
        try:
            return store().save(payload)
        except ContentError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.put("/{slug}", response_model=ContentItem, dependencies=[Depends(require_admin)])
    def update_item(slug: str, payload: ContentWrite):
        try:
            return store().save(payload, old_slug=slug)
        except ContentError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.delete("/{slug}", dependencies=[Depends(require_admin)])
    def delete_item(slug: str):
        try:
            store().delete(slug)
            return {"ok": True}
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="内容不存在")

    return router
