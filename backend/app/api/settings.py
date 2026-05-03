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
        normalized[key] = min(1.0, max(0.6, number))
    return normalized


def _theme_config_with_defaults(value: Any) -> dict[str, Any]:
    theme_config = deepcopy(value) if isinstance(value, dict) else {}
    theme_config["opacity"] = _normalize_opacity(theme_config.get("opacity"))
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
