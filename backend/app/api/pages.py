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


def _component(
    order: int,
    w: float,
    h: float,
    label: str,
    component_type: str,
    *,
    row_span: float = 1,
    visible: bool = True,
    locked: bool = True,
    props: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "order": order,
        "w": w,
        "h": h,
        "rowSpan": row_span,
        "visible": visible,
        "label": label,
        "type": component_type,
        "locked": locked,
        "props": props or {},
    }


DEFAULT_PAGE_TEXT: dict[str, dict[str, str]] = {
    "home": {"title": "首页", "subtitle": "名片、音乐、歌词、轮播与状态区。"},
    "posts": {"title": "文章归档", "subtitle": "从 FastAPI 读取 Markdown 内容，草稿默认不会出现在公开列表。"},
    "chatters": {"title": "云端杂谈", "subtitle": "长一点的念头，短一点的文章。"},
    "photos": {"title": "图片", "subtitle": "相册记录从后端 JSON 动态读取，点击封面可查看组内照片。"},
    "music": {"title": "音乐歌单", "subtitle": "全局播放器、歌词和歌单共享同一播放状态。"},
    "projects": {"title": "项目陈列柜", "subtitle": "记录正在构建和已经完成的作品。"},
    "friends": {"title": "星际友链", "subtitle": "把值得长期访问的站点放在这里。"},
    "about": {"title": "关于", "subtitle": "关于 SRBlogs 与站点作者。"},
}


DEFAULT_PAGE_LAYOUTS: dict[str, dict[str, Any]] = {
    "home": {
        "layoutVersion": 1,
        "components": {
            "profileCard": _component(1, 6, 2, "名片", "profileCard"),
            "musicPlayer": _component(2, 6, 2, "音乐播放器", "musicPlayer"),
            "lyrics": _component(3, 12, 1, "歌词区", "lyrics"),
            "latestPostsCarousel": _component(4, 4, 3, "最新文章轮播", "latestPostsCarousel"),
            "photoCarousel": _component(5, 8, 2, "图片轮播", "photoCarousel"),
            "updatesCarousel": _component(6, 8, 2, "更新内容轮播", "updatesCarousel"),
            "themeToggle": _component(7, 4, 2, "昼夜切换卡片", "themeToggle"),
            "statusBar": _component(8, 12, 1, "底部状态区", "statusBar"),
        },
    },
    "posts": {
        "layoutVersion": 1,
        "components": {
            "pageTitle": _component(1, 12, 1.4, "页面标题区", "pageTitle"),
            "sectionSwitch": _component(2, 12, 0.8, "正经 / 杂谈切换", "sectionSwitch"),
            "searchBox": _component(3, 12, 0.8, "搜索区", "searchBox"),
            "tagFilter": _component(4, 12, 0.8, "标签筛选区", "tagFilter"),
            "viewModeSwitch": _component(5, 12, 0.8, "显示模式切换", "viewModeSwitch"),
            "contentList": _component(6, 12, 4, "内容列表区", "contentList"),
        },
    },
    "photos": {
        "layoutVersion": 1,
        "components": {
            "pageTitle": _component(1, 12, 1.4, "页面标题区", "pageTitle"),
            "viewModeSwitch": _component(2, 12, 0.8, "显示模式切换", "viewModeSwitch"),
            "albumList": _component(3, 12, 4, "相册列表区", "albumList"),
            "messageBoard": _component(4, 12, 2, "留言板区域", "messageBoard", visible=False),
        },
    },
    "music": {
        "layoutVersion": 1,
        "components": {
            "pageTitle": _component(1, 12, 1.4, "页面标题区", "pageTitle"),
            "playerPanel": _component(2, 5, 4, "音乐播放器面板", "playerPanel"),
            "lyricsPlaylistPanel": _component(3, 7, 4, "歌词 / 歌单面板", "lyricsPlaylistPanel"),
            "messageBoard": _component(4, 12, 2, "留言板", "messageBoard"),
        },
    },
    "projects": {
        "layoutVersion": 1,
        "components": {
            "pageTitle": _component(1, 12, 1.4, "页面标题区", "pageTitle"),
            "projectList": _component(2, 12, 4, "项目列表区", "projectList"),
        },
    },
    "friends": {
        "layoutVersion": 1,
        "components": {
            "pageTitle": _component(1, 12, 1.4, "页面标题区", "pageTitle"),
            "friendList": _component(2, 12, 4, "友链列表区", "friendList"),
        },
    },
    "about": {
        "layoutVersion": 1,
        "components": {
            "pageTitle": _component(1, 12, 1.4, "页面标题区", "pageTitle"),
            "markdownContent": _component(2, 12, 4, "Markdown 内容区", "markdownContent"),
        },
    },
}


DEFAULT_PAGE_CONFIG: dict[str, Any] = {
    "pageText": deepcopy(DEFAULT_PAGE_TEXT),
    "homeProfile": {
        "author": "",
        "avatar": "",
        "description": "",
        "socialLinks": {"github": "", "email": "", "qq": "", "wechat": ""},
    },
    "pageLayouts": deepcopy(DEFAULT_PAGE_LAYOUTS),
    "homeLayout": deepcopy(DEFAULT_PAGE_LAYOUTS["home"]),
    "home": deepcopy(DEFAULT_PAGE_LAYOUTS["home"]),
}

DEFAULT_PAGE_LAYOUTS["home"]["components"].update(
    {
        "profileCard": _component(1, 6, 2, "名片", "profileCard"),
        "musicPlayer": _component(2, 6, 2, "音乐播放器", "musicPlayer"),
        "lyrics": _component(3, 12, 1, "歌词区", "lyrics"),
        "latestPostsCarousel": _component(4, 4, 4, "最新文章轮播", "latestPostsCarousel", row_span=2),
        "photoCarousel": _component(5, 8, 2, "图片轮播", "photoCarousel"),
        "updatesCarousel": _component(6, 4, 2, "更新内容轮播", "updatesCarousel"),
        "themeToggle": _component(7, 4, 2, "昼夜切换卡片", "themeToggle"),
        "statusBar": _component(8, 12, 1, "底部状态区", "statusBar"),
    }
)
DEFAULT_PAGE_CONFIG["pageLayouts"] = deepcopy(DEFAULT_PAGE_LAYOUTS)
DEFAULT_PAGE_CONFIG["homeLayout"] = deepcopy(DEFAULT_PAGE_LAYOUTS["home"])
DEFAULT_PAGE_CONFIG["home"] = deepcopy(DEFAULT_PAGE_LAYOUTS["home"])


def _store() -> JsonStore:
    return JsonStore(get_settings().data_path, "page_config.json", DEFAULT_PAGE_CONFIG)


def _settings_store() -> JsonStore:
    return JsonStore(get_settings().data_path, "settings.json", {})


def _number(value: Any, fallback: float, min_value: float, max_value: float) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        result = fallback
    return round(min(max(result, min_value), max_value), 2)


def _normalize_component(component_id: str, saved: dict[str, Any] | None, default: dict[str, Any] | None = None) -> dict[str, Any]:
    base = deepcopy(default or _component(99, 12, 1, component_id, saved.get("type", "customText") if isinstance(saved, dict) else "customText", locked=False))
    saved = saved if isinstance(saved, dict) else {}
    base.update({k: v for k, v in saved.items() if k not in {"w", "h", "rowSpan", "order", "visible", "props"}})
    base["order"] = int(_number(saved.get("order"), base.get("order", 99), 1, 999))
    base["w"] = _number(saved.get("w"), base.get("w", 12), 1, 12)
    base["h"] = _number(saved.get("h"), base.get("h", 1), 0.5, 8)
    base["rowSpan"] = int(_number(saved.get("rowSpan"), base.get("rowSpan", 1), 1, 4))
    base["visible"] = saved.get("visible", base.get("visible", True)) is not False
    base["props"] = saved.get("props") if isinstance(saved.get("props"), dict) else base.get("props", {})
    base["label"] = str(base.get("label") or component_id)
    base["type"] = str(base.get("type") or component_id)
    return base


def _merge_layout(page_key: str, saved_layout: Any) -> dict[str, Any]:
    default_layout = deepcopy(DEFAULT_PAGE_LAYOUTS.get(page_key, {"layoutVersion": 1, "components": {}}))
    saved_layout = saved_layout if isinstance(saved_layout, dict) else {}
    default_components = default_layout.get("components", {})
    saved_components = saved_layout.get("components") if isinstance(saved_layout.get("components"), dict) else {}

    components: dict[str, Any] = {}
    for component_id, default_component in default_components.items():
        components[component_id] = _normalize_component(component_id, saved_components.get(component_id), default_component)

    for component_id, saved_component in saved_components.items():
        if component_id not in components:
            components[component_id] = _normalize_component(component_id, saved_component, None)

    if page_key == "home":
        for component_id in ("latestPostsCarousel", "photoCarousel", "updatesCarousel", "themeToggle"):
            saved_component = saved_components.get(component_id)
            default_component = default_components.get(component_id)
            if isinstance(saved_component, dict) and default_component and "rowSpan" not in saved_component:
                components[component_id]["w"] = default_component.get("w", components[component_id].get("w", 12))
                components[component_id]["h"] = default_component.get("h", components[component_id].get("h", 1))
                components[component_id]["rowSpan"] = default_component.get("rowSpan", components[component_id].get("rowSpan", 1))

    default_layout["layoutVersion"] = max(2 if page_key == "home" else 1, int(saved_layout.get("layoutVersion") or saved_layout.get("layout_version") or default_layout.get("layoutVersion") or 1))
    default_layout["components"] = components
    return default_layout


def _merge_defaults(data: dict[str, Any]) -> dict[str, Any]:
    source = deepcopy(data or {})
    merged = deepcopy(DEFAULT_PAGE_CONFIG)

    compact_home = source.pop("home", None)
    if isinstance(compact_home, dict) and "homeLayout" not in source:
        source["homeLayout"] = {
            "layoutVersion": compact_home.get("layoutVersion", compact_home.get("layout_version", 1)),
            "components": compact_home.get("components", {}),
        }

    saved_page_text = source.get("pageText") if isinstance(source.get("pageText"), dict) else {}
    for key, value in saved_page_text.items():
        if isinstance(value, dict):
            merged["pageText"].setdefault(key, {})
            merged["pageText"][key].update(value)

    if isinstance(source.get("homeProfile"), dict):
        merged["homeProfile"].update(source["homeProfile"])

    saved_layouts = source.get("pageLayouts") if isinstance(source.get("pageLayouts"), dict) else {}
    if isinstance(source.get("homeLayout"), dict):
        saved_layouts = {**saved_layouts, "home": source["homeLayout"]}

    page_layouts: dict[str, Any] = {}
    for page_key in DEFAULT_PAGE_LAYOUTS.keys():
        page_layouts[page_key] = _merge_layout(page_key, saved_layouts.get(page_key))
    for page_key, saved_layout in saved_layouts.items():
        if page_key not in page_layouts:
            page_layouts[page_key] = _merge_layout(page_key, saved_layout)

    merged["pageLayouts"] = page_layouts
    merged["homeLayout"] = deepcopy(page_layouts["home"])
    merged["home"] = deepcopy(page_layouts["home"])

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
    write_audit(
        actor=actor,
        action="pages.config.update",
        resource="pages",
        target="page_config.json",
        result="success",
        message="Page config updated",
    )
    return data
