from __future__ import annotations

from copy import deepcopy
from typing import Any

from fastapi import APIRouter, Depends

from app.config import get_settings
from app.models.schemas import JsonWrite
from app.services.auth_service import require_admin
from app.services.json_service import JsonStore

router = APIRouter(tags=["settings"])

PUBLIC_KEYS = {
    "title",
    "authorName",
    "bio",
    "avatarUrl",
    "defaultPostCover",
    "photoWallImage",
    "bgImages",
    "themeColors",
    "cloudMusicIds",
    "danmakuList",
    "social",
    "counts",
    "chatterTitle",
    "chatterDescription",
    "buildDate",
    "theme",
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


def public_settings(data: dict[str, Any]) -> dict[str, Any]:
    public = {key: deepcopy(data[key]) for key in PUBLIC_KEYS if key in data}
    gitalk = data.get("gitalkConfig")
    if isinstance(gitalk, dict):
        public["gitalkConfig"] = {
            "clientID": gitalk.get("clientID", ""),
            "repo": gitalk.get("repo", ""),
            "owner": gitalk.get("owner", ""),
            "admin": gitalk.get("admin", []),
            "clientSecretConfigured": _configured(gitalk.get("clientSecret", "")),
        }
    return public


def admin_settings(data: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(data)
    gitalk = result.get("gitalkConfig")
    if isinstance(gitalk, dict):
        gitalk["clientSecretConfigured"] = _configured(gitalk.pop("clientSecret", ""))
    image_bed = result.get("imageBed")
    if isinstance(image_bed, dict):
        token = image_bed.pop("token", "") or image_bed.pop("accessKeySecret", "")
        image_bed["ossKeyConfigured"] = _configured(token)
    ai = result.get("ai")
    if isinstance(ai, dict):
        for key in list(ai.keys()):
            if "key" in key.lower() or "secret" in key.lower() or "token" in key.lower():
                ai.pop(key, None)
        ai["aiKeyConfigured"] = bool(get_settings().ai_a_api_key or get_settings().ai_b_api_key)
    else:
        result["ai"] = {"aiKeyConfigured": bool(get_settings().ai_a_api_key or get_settings().ai_b_api_key)}
    result["serverSecrets"] = {
        "jwtSecretConfigured": _configured(get_settings().jwt_secret),
        "adminPasswordConfigured": _configured(get_settings().admin_password),
        "ossKeyConfigured": _configured(get_settings().oss_access_key_secret),
        "aiKeyConfigured": _configured(get_settings().ai_a_api_key or get_settings().ai_b_api_key),
        "githubOAuthSecretConfigured": _configured((data.get("gitalkConfig") or {}).get("clientSecret", "")),
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
    ai = cleaned.get("ai")
    if isinstance(ai, dict):
        ai.pop("aiKeyConfigured", None)
    return cleaned


@router.get("/settings/public")
def read_public_settings():
    return public_settings(_store().read())


@router.get("/admin/settings", dependencies=[Depends(require_admin)])
def read_admin_settings():
    return admin_settings(_store().read())


@router.put("/admin/settings", dependencies=[Depends(require_admin)])
def write_admin_settings(payload: JsonWrite):
    current = _store().read()
    incoming = _strip_computed_fields(payload.data) if isinstance(payload.data, dict) else {}
    for secret_section, secret_key in (
        ("gitalkConfig", "clientSecret"),
        ("imageBed", "token"),
        ("imageBed", "accessKeySecret"),
    ):
        if isinstance(current.get(secret_section), dict) and isinstance(incoming.get(secret_section), dict):
            value = current[secret_section].get(secret_key)
            if value and not incoming[secret_section].get(secret_key):
                incoming[secret_section][secret_key] = value
    _store().write(incoming)
    return admin_settings(incoming)
