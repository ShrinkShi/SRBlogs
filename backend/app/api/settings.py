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


def public_settings(data: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    comments = deepcopy(data.get("comments") or {})
    gitalk = deepcopy(data.get("gitalkConfig") or comments.get("gitalk") or {})
    public_comments = {
        "enabled": comments.get("enabled", True),
        "requireEmail": comments.get("requireEmail", False),
        "maxLength": comments.get("maxLength", 1000),
        "showEmail": comments.get("showEmail", False),
        "localEnabled": comments.get("localEnabled", True),
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
        "themeConfig": deepcopy(data.get("themeConfig") or {}),
        "bgImages": deepcopy(data.get("bgImages") or []),
        "cloudMusicIds": deepcopy(data.get("cloudMusicIds") or []),
        "interaction": deepcopy(data.get("interaction") or {"clickSoundEnabled": True, "clickSoundVolume": 0.05, "clickSoundUrl": ""}),
        "githubOAuth": {
            "configured": bool(settings.github_oauth_client_id and settings.github_oauth_client_secret),
        },
        "comments": public_comments,
    }


def admin_settings(data: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(data)
    gitalk = result.get("gitalkConfig")
    if isinstance(gitalk, dict):
        gitalk["clientSecretConfigured"] = _configured(gitalk.pop("clientSecret", ""))
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
        "githubOAuthSecretConfigured": _configured((data.get("gitalkConfig") or {}).get("clientSecret", "")),
        "githubOAuthConfigured": _configured(get_settings().github_oauth_client_id and get_settings().github_oauth_client_secret),
    }
    return result


def _strip_computed_fields(data: dict[str, Any]) -> dict[str, Any]:
    cleaned = deepcopy(data)
    cleaned.pop("serverSecrets", None)
    gitalk = cleaned.get("gitalkConfig")
    if isinstance(gitalk, dict):
        gitalk.pop("clientSecretConfigured", None)
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
            if current_value and (incoming_value is None or incoming_value == ""):
                incoming_section[secret_key] = current_value
    try:
        _store().write(incoming)
        write_audit(actor=actor, action="settings.update", resource="settings", target="settings.json", result="success", message="Settings updated")
        return admin_settings(incoming)
    except Exception as exc:
        write_audit(actor=actor, action="settings.update", resource="settings", target="settings.json", result="failed", message=str(exc))
        raise
