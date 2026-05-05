from __future__ import annotations

from copy import deepcopy
from typing import Any

from fastapi import APIRouter, Depends

from app.config import get_settings
from app.models.schemas import JsonWrite
from app.services.audit_service import write_audit
from app.services.auth_service import require_admin
from app.services.json_service import JsonStore

router = APIRouter(tags=["settings"])

DEFAULT_OPACITY: dict[str, float] = {
    "toolboxSettingsPanel": 0.92,
    "toolboxSearchPanel": 0.92,
    "toolboxCalculatorPanel": 0.90,
    "homeCard": 0.82,
    "homeCarousel": 0.82,
    "contentCard": 0.82,
    "photoCard": 0.82,
    "musicPanel": 0.88,
    "messageBoard": 0.86,
    "navBar": 0.72,
}

COMPONENT_THEME_LABELS: dict[str, str] = {
    "topNav": "顶部导航栏",
    "toolboxFab": "左下角工具箱悬浮球",
    "toolboxMenu": "工具箱菜单",
    "toolboxSettingsPanel": "工具箱设置弹窗",
    "toolboxSearchPanel": "工具箱全局搜索弹窗",
    "toolboxCalculatorPanel": "工具箱计算器弹窗",
    "toast": "Toast 提示",
    "homeProfileCard": "首页名片",
    "homeMusicPlayer": "首页音乐播放器",
    "homeLyrics": "首页歌词区",
    "homeLatestPostsCarousel": "首页最新文章轮播",
    "homePhotoCarousel": "首页图片轮播",
    "homeUpdatesCarousel": "首页更新内容轮播",
    "homeThemeToggle": "首页昼夜切换卡片",
    "homeStatusBar": "首页底部状态区",
    "sectionSwitch": "正经 / 杂谈切换按钮",
    "viewModeSwitch": "矩阵网格 / 中枢链路切换按钮",
    "postCard": "文章卡片",
    "chatterCard": "杂谈卡片",
    "photoAlbumCard": "图片相册卡片",
    "musicPlayerPanel": "音乐页播放器面板",
    "musicLyricsPanel": "音乐页歌词/歌单面板",
    "messageBoard": "留言板",
    "searchInput": "搜索框",
    "searchButton": "搜索按钮",
    "tagButton": "标签按钮",
}


def _default_component_theme() -> dict[str, dict[str, Any]]:
    def item(label: str, opacity: float = 0.86) -> dict[str, Any]:
        return {
            "label": label,
            "day": {
                "bg": "rgba(255,255,255,.9)",
                "text": "rgba(17,24,39,.94)",
                "accent": "#dc2626",
                "border": "rgba(17,24,39,.14)",
            },
            "night": {
                "bg": "rgba(18,18,18,.88)",
                "text": "rgba(249,250,251,.94)",
                "accent": "#f87171",
                "border": "rgba(255,255,255,.16)",
            },
            "opacity": opacity,
            "size": "medium",
            "fontFamily": "",
            "fontSize": 16,
            "textColor": "",
            "textAlign": "left",
            "fontWeight": "normal",
            "fontStyle": "normal",
        }

    opacity_overrides = {
        "topNav": DEFAULT_OPACITY["navBar"],
        "toolboxSettingsPanel": DEFAULT_OPACITY["toolboxSettingsPanel"],
        "toolboxSearchPanel": DEFAULT_OPACITY["toolboxSearchPanel"],
        "toolboxCalculatorPanel": DEFAULT_OPACITY["toolboxCalculatorPanel"],
        "homeProfileCard": DEFAULT_OPACITY["homeCard"],
        "homeMusicPlayer": DEFAULT_OPACITY["homeCard"],
        "homeLyrics": DEFAULT_OPACITY["homeCard"],
        "homeLatestPostsCarousel": DEFAULT_OPACITY["homeCarousel"],
        "homePhotoCarousel": DEFAULT_OPACITY["homeCarousel"],
        "homeUpdatesCarousel": DEFAULT_OPACITY["homeCarousel"],
        "homeThemeToggle": DEFAULT_OPACITY["homeCard"],
        "homeStatusBar": DEFAULT_OPACITY["homeCard"],
        "postCard": DEFAULT_OPACITY["contentCard"],
        "chatterCard": DEFAULT_OPACITY["contentCard"],
        "photoAlbumCard": DEFAULT_OPACITY["photoCard"],
        "musicPlayerPanel": DEFAULT_OPACITY["musicPanel"],
        "musicLyricsPanel": DEFAULT_OPACITY["musicPanel"],
        "messageBoard": DEFAULT_OPACITY["messageBoard"],
    }
    return {
        key: item(label, opacity_overrides.get(key, 0.86))
        for key, label in COMPONENT_THEME_LABELS.items()
    }


DEFAULT_COMPONENT_THEME = _default_component_theme()


def _store() -> JsonStore:
    return JsonStore(get_settings().data_path, "settings.json", {})


def _configured(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(_configured(item) for item in value)
    if isinstance(value, dict):
        return any(_configured(item) for item in value.values())
    return bool(value)


def _normalize_opacity(value: Any) -> dict[str, float]:
    source = value if isinstance(value, dict) else {}
    normalized = deepcopy(DEFAULT_OPACITY)
    for key in DEFAULT_OPACITY:
        try:
            number = float(source.get(key, normalized[key]))
        except (TypeError, ValueError):
            number = normalized[key]
        normalized[key] = min(1.0, max(0.0, number))
    return normalized


def _normalize_component_theme(value: Any) -> dict[str, dict[str, Any]]:
    source = value if isinstance(value, dict) else {}
    normalized = deepcopy(DEFAULT_COMPONENT_THEME)
    for key, fallback in DEFAULT_COMPONENT_THEME.items():
        incoming = source.get(key)
        if not isinstance(incoming, dict):
            continue
        item = normalized[key]
        item["label"] = str(incoming.get("label") or fallback["label"])
        for mode in ("day", "night"):
            mode_source = incoming.get(mode)
            if isinstance(mode_source, dict):
                item[mode] = {**item[mode], **{k: str(v) for k, v in mode_source.items() if v is not None}}
        try:
            opacity = float(incoming.get("opacity", item["opacity"]))
        except (TypeError, ValueError):
            opacity = item["opacity"]
        item["opacity"] = min(1.0, max(0.0, opacity))
        size = str(incoming.get("size") or item["size"])
        item["size"] = size if size in {"small", "medium", "large"} else "medium"
        item["fontFamily"] = str(incoming.get("fontFamily") or item.get("fontFamily") or "")
        try:
            font_size = float(incoming.get("fontSize", item.get("fontSize", 16)))
        except (TypeError, ValueError):
            font_size = 16
        item["fontSize"] = min(64, max(8, font_size))
        item["textColor"] = str(incoming.get("textColor") or item.get("textColor") or "")
        text_align = str(incoming.get("textAlign") or item.get("textAlign") or "left")
        item["textAlign"] = text_align if text_align in {"left", "center", "right"} else "left"
        item["fontWeight"] = str(incoming.get("fontWeight") or item.get("fontWeight") or "normal")
        item["fontStyle"] = str(incoming.get("fontStyle") or item.get("fontStyle") or "normal")
    return normalized


def _theme_config_with_defaults(value: Any) -> dict[str, Any]:
    theme_config = deepcopy(value) if isinstance(value, dict) else {}
    theme_config["opacity"] = _normalize_opacity(theme_config.get("opacity"))
    theme_config["componentTheme"] = _normalize_component_theme(theme_config.get("componentTheme"))
    return theme_config


def public_settings(data: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    interaction = {
        "clickSoundEnabled": True,
        "clickSoundVolume": 0.05,
        "clickSoundUrl": "",
        "clickEffectEnabled": True,
        **deepcopy(data.get("interaction") or {}),
    }
    comments = deepcopy(data.get("comments") or {})
    gitalk = deepcopy(data.get("gitalkConfig") or comments.get("gitalk") or {})
    github_client_id = settings.github_oauth_client_id or gitalk.get("clientID", "")
    github_client_secret = settings.github_oauth_client_secret or gitalk.get("clientSecret", "")
    github_client_id_configured = _configured(github_client_id)
    github_secret_configured = _configured(github_client_secret)
    github_login_configured = github_client_id_configured and github_secret_configured
    github_login_enabled = comments.get("githubLoginEnabled", comments.get("githubEnabled", True)) is not False
    qq = deepcopy(data.get("qqOAuth") or comments.get("qq") or {})
    qq_app_id = settings.qq_oauth_app_id or qq.get("appID", "") or qq.get("appId", "") or qq.get("clientID", "")
    qq_app_secret = settings.qq_oauth_app_secret or qq.get("appSecret", "") or qq.get("clientSecret", "")
    qq_app_id_configured = _configured(qq_app_id)
    qq_secret_configured = _configured(qq_app_secret)
    qq_login_configured = qq_app_id_configured and qq_secret_configured
    qq_login_enabled = comments.get("qqLoginEnabled", True) is not False
    public_comments = {
        "enabled": comments.get("enabled", True),
        "provider": "multi",
        "providers": {
            "github": {
                "enabled": github_login_enabled,
                "configured": github_login_configured,
                "clientIdConfigured": github_client_id_configured,
                "secretConfigured": github_secret_configured,
            },
            "qq": {
                "enabled": qq_login_enabled,
                "configured": qq_login_configured,
                "appIdConfigured": qq_app_id_configured,
                "secretConfigured": qq_secret_configured,
            },
        },
        "githubLoginEnabled": github_login_enabled,
        "githubLoginConfigured": github_login_configured,
        "qqLoginEnabled": qq_login_enabled,
        "qqLoginConfigured": qq_login_configured,
        "maxLength": comments.get("maxLength", 1000),
        "gitalk": {
            "clientID": gitalk.get("clientID", ""),
            "repo": gitalk.get("repo", ""),
            "owner": gitalk.get("owner", ""),
            "admin": gitalk.get("admin", []),
        },
    }
    return {
        "siteTitle": data.get("siteTitle") or data.get("title", "SRBlogs"),
        "subtitle": data.get("subtitle", ""),
        "author": data.get("author") or data.get("authorName", ""),
        "avatar": data.get("avatar") or data.get("avatarUrl", ""),
        "description": data.get("description") or data.get("bio", ""),
        "socialLinks": deepcopy(data.get("socialLinks") or data.get("social") or {}),
        "theme": data.get("theme", "nebula"),
        "themeConfig": _theme_config_with_defaults(data.get("themeConfig")),
        "bgImages": deepcopy(data.get("bgImages") or []),
        "cloudMusicIds": deepcopy(data.get("cloudMusicIds") or []),
        "interaction": interaction,
        "pageText": deepcopy(data.get("pageText") or {}),
        "pageLayouts": deepcopy(data.get("pageLayouts") or {}),
        "githubOAuth": {
            "configured": github_login_configured,
            "clientIdConfigured": github_client_id_configured,
            "secretConfigured": github_secret_configured,
        },
        "qqOAuth": {
            "configured": qq_login_configured,
            "appIdConfigured": qq_app_id_configured,
            "secretConfigured": qq_secret_configured,
        },
        "comments": public_comments,
    }


def admin_settings(data: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(data)
    result["themeConfig"] = _theme_config_with_defaults(result.get("themeConfig"))
    gitalk = result.get("gitalkConfig")
    if isinstance(gitalk, dict):
        gitalk["clientSecretConfigured"] = _configured(gitalk.pop("clientSecret", ""))
    qq_oauth = result.get("qqOAuth")
    if isinstance(qq_oauth, dict):
        qq_secret = qq_oauth.pop("appSecret", "") or qq_oauth.pop("clientSecret", "")
        qq_oauth["appSecretConfigured"] = _configured(qq_secret)
    image_bed = result.get("imageBed")
    if isinstance(image_bed, dict):
        access_key = image_bed.pop("accessKeyId", "") or image_bed.pop("accessKey", "")
        secret_key = image_bed.pop("token", "") or image_bed.pop("accessKeySecret", "") or image_bed.pop("secretKey", "")
        image_bed["accessKeyConfigured"] = _configured(access_key)
        image_bed["secretKeyConfigured"] = _configured(secret_key)
        image_bed["ossKeyConfigured"] = _configured(access_key or secret_key)
    ai = result.get("ai")
    if isinstance(ai, dict):
        stored_ai_key = ""
        for key in list(ai.keys()):
            if "key" in key.lower() or "secret" in key.lower() or "token" in key.lower():
                stored_ai_key = stored_ai_key or ai.get(key, "")
                ai.pop(key, None)
        ai["aiKeyConfigured"] = _configured(stored_ai_key or get_settings().ai_a_api_key or get_settings().ai_b_api_key)
    else:
        result["ai"] = {"aiKeyConfigured": bool(get_settings().ai_a_api_key or get_settings().ai_b_api_key)}
    result["serverSecrets"] = {
        "jwtSecretConfigured": _configured(get_settings().jwt_secret),
        "adminPasswordConfigured": _configured(get_settings().admin_password),
        "ossKeyConfigured": _configured(get_settings().oss_access_key_secret),
        "aiKeyConfigured": _configured(get_settings().ai_a_api_key or get_settings().ai_b_api_key),
        "githubOAuthClientIdConfigured": _configured(get_settings().github_oauth_client_id or (data.get("gitalkConfig") or {}).get("clientID", "")),
        "githubOAuthSecretConfigured": _configured(get_settings().github_oauth_client_secret or (data.get("gitalkConfig") or {}).get("clientSecret", "")),
        "githubOAuthConfigured": _configured(
            (get_settings().github_oauth_client_id or (data.get("gitalkConfig") or {}).get("clientID", ""))
            and (get_settings().github_oauth_client_secret or (data.get("gitalkConfig") or {}).get("clientSecret", ""))
        ),
        "qqOAuthAppIdConfigured": _configured(get_settings().qq_oauth_app_id or (data.get("qqOAuth") or {}).get("appID", "") or (data.get("qqOAuth") or {}).get("appId", "")),
        "qqOAuthSecretConfigured": _configured(get_settings().qq_oauth_app_secret or (data.get("qqOAuth") or {}).get("appSecret", "")),
        "qqOAuthConfigured": _configured(
            (get_settings().qq_oauth_app_id or (data.get("qqOAuth") or {}).get("appID", "") or (data.get("qqOAuth") or {}).get("appId", ""))
            and (get_settings().qq_oauth_app_secret or (data.get("qqOAuth") or {}).get("appSecret", ""))
        ),
    }
    return result


def _strip_computed_fields(data: dict[str, Any]) -> dict[str, Any]:
    cleaned = deepcopy(data)
    cleaned.pop("serverSecrets", None)
    gitalk = cleaned.get("gitalkConfig")
    if isinstance(gitalk, dict):
        gitalk.pop("clientSecretConfigured", None)
    qq_oauth = cleaned.get("qqOAuth")
    if isinstance(qq_oauth, dict):
        qq_oauth.pop("appSecretConfigured", None)
    image_bed = cleaned.get("imageBed")
    if isinstance(image_bed, dict):
        image_bed.pop("ossKeyConfigured", None)
        image_bed.pop("accessKeyConfigured", None)
        image_bed.pop("secretKeyConfigured", None)
    ai = cleaned.get("ai")
    if isinstance(ai, dict):
        ai.pop("aiKeyConfigured", None)
    interaction = cleaned.get("interaction")
    if isinstance(interaction, dict):
        interaction.pop("clickSoundConfigured", None)
    return cleaned


@router.get("/settings/public")
def read_public_settings():
    return public_settings(_store().read())


@router.get("/admin/settings", dependencies=[Depends(require_admin)])
def read_admin_settings():
    return admin_settings(_store().read())


@router.put("/admin/settings")
def write_admin_settings(payload: JsonWrite, actor: str = Depends(require_admin)):
    current = _store().read()
    incoming = _strip_computed_fields(payload.data) if isinstance(payload.data, dict) else {}
    for secret_section, secret_key in (
        ("gitalkConfig", "clientSecret"),
        ("qqOAuth", "appSecret"),
        ("qqOAuth", "clientSecret"),
        ("imageBed", "accessKeyId"),
        ("imageBed", "accessKey"),
        ("imageBed", "token"),
        ("imageBed", "accessKeySecret"),
        ("imageBed", "secretKey"),
        ("ai", "apiKey"),
        ("ai", "key"),
    ):
        current_section = current.get(secret_section)
        incoming_section = incoming.get(secret_section)
        if isinstance(current_section, dict) and isinstance(incoming_section, dict):
            current_value = current_section.get(secret_key)
            incoming_value = incoming_section.get(secret_key)
            if secret_key in current_section and (incoming_value is None or incoming_value == ""):
                incoming_section[secret_key] = current_value
    try:
        _store().write(incoming)
        write_audit(actor=actor, action="settings.update", resource="settings", target="settings.json", result="success", message="Settings updated")
        return admin_settings(incoming)
    except Exception as exc:
        write_audit(actor=actor, action="settings.update", resource="settings", target="settings.json", result="failed", message=str(exc))
        raise
