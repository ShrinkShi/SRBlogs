from __future__ import annotations

from copy import deepcopy
from typing import Any

from fastapi import APIRouter, Depends

from app.config import get_settings
from app.models.schemas import JsonWrite
from app.services.audit_service import write_audit
from app.services.auth_service import require_admin
from app.services.json_service import JsonStore

router = APIRouter(tags=["pages"])


DEFAULT_PAGE_CONFIG: dict[str, Any] = {
    "pageText": {
        "home": {"title": "首页", "subtitle": "名片、音乐、歌词、轮播与状态区。"},
        "posts": {"title": "文章归档", "subtitle": "从 FastAPI 读取 Markdown 内容，草稿默认不会出现在公开列表。"},
        "chatters": {"title": "云端杂谈", "subtitle": "长一点的念头，短一点的文章。"},
        "photos": {"title": "图片", "subtitle": "相册记录从后端 JSON 动态读取，点击封面可查看组内照片。"},
        "music": {"title": "音乐歌单", "subtitle": "全局播放器、歌词和歌单共享同一播放状态。"},
        "projects": {"title": "项目陈列柜", "subtitle": "记录正在构建和已经完成的作品。"},
        "friends": {"title": "星际友链", "subtitle": "把值得长期访问的站点放在这里。"},
        "about": {"title": "关于", "subtitle": "关于 SRBlogs 与站点作者。"},
    },
    "homeProfile": {
        "author": "",
        "avatar": "",
        "description": "",
        "socialLinks": {"github": "", "email": "", "qq": "", "wechat": ""},
    },
    "homeLayout": {
        "layoutVersion": 1,
        "components": {
            "profileCard": {"order": 1, "w": 6, "h": 2, "visible": True},
            "musicPlayer": {"order": 2, "w": 6, "h": 2, "visible": True},
            "lyrics": {"order": 3, "w": 12, "h": 1, "visible": True},
            "latestPostsCarousel": {"order": 4, "w": 4, "h": 3, "visible": True},
            "photoCarousel": {"order": 5, "w": 8, "h": 2, "visible": True},
            "updatesCarousel": {"order": 6, "w": 8, "h": 2, "visible": True},
            "themeToggle": {"order": 7, "w": 4, "h": 2, "visible": True},
            "statusBar": {"order": 8, "w": 12, "h": 1, "visible": True},
        },
    },
}


def _store() -> JsonStore:
    return JsonStore(get_settings().data_path, "page_config.json", DEFAULT_PAGE_CONFIG)


def _settings_store() -> JsonStore:
    return JsonStore(get_settings().data_path, "settings.json", {})


def _merge_defaults(data: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(DEFAULT_PAGE_CONFIG)
    source = deepcopy(data or {})
    # Accept the documented compact shape as an alias while keeping the
    # established frontend/admin contract (`homeLayout`) stable.
    compact_home = source.pop("home", None)
    if isinstance(compact_home, dict) and "homeLayout" not in source:
        source["homeLayout"] = {
            "layoutVersion": compact_home.get("layoutVersion", compact_home.get("layout_version", 1)),
            "components": compact_home.get("components", {}),
        }
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    settings = _settings_store().read()
    profile = merged.setdefault("homeProfile", {})
    if not profile.get("author"):
        profile["author"] = settings.get("author") or settings.get("authorName") or ""
    if not profile.get("avatar"):
        profile["avatar"] = settings.get("avatar") or settings.get("avatarUrl") or ""
    if not profile.get("description"):
        profile["description"] = settings.get("description") or settings.get("bio") or ""
    if not profile.get("socialLinks"):
        profile["socialLinks"] = settings.get("socialLinks") or settings.get("social") or {}
    merged["home"] = deepcopy(merged.get("homeLayout") or {})
    return merged


def _public_config() -> dict[str, Any]:
    return _merge_defaults(_store().read())


@router.get("/pages/config")
def read_public_pages_config():
    return _public_config()


@router.get("/admin/pages/config", dependencies=[Depends(require_admin)])
def read_admin_pages_config():
    return _public_config()


@router.put("/admin/pages/config")
def write_admin_pages_config(payload: JsonWrite, actor: str = Depends(require_admin)):
    incoming = payload.data if isinstance(payload.data, dict) else {}
    data = _merge_defaults(incoming)
    _store().write(data)
    write_audit(actor=actor, action="pages.config.update", resource="pages", target="page_config.json", result="success", message="Page config updated")
    return data
