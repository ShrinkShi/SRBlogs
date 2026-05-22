from __future__ import annotations

import os
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.services.admin_credentials import hash_admin_password
from app.services.file_store import safe_read_json, safe_write_json, safe_write_text

INSTALL_VERSION = "1"
INSTALL_LOCK = ".install.lock"
FAIL_WINDOW_SECONDS = 600
MAX_FAILED_ATTEMPTS = 5
WEAK_PASSWORDS = {
    "admin",
    "change-me",
    "changeme",
    "123456",
    "12345678",
    "123456789",
    "password",
    "password123",
    "admin123",
    "qwerty123",
}

_failed_attempts: dict[str, list[float]] = {}


class InstallError(ValueError):
    pass


class InstallRateLimitError(InstallError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def data_path() -> Path:
    return get_settings().data_path


def install_lock_path() -> Path:
    return data_path() / INSTALL_LOCK


def env_path() -> Path:
    raw = os.environ.get("ENV_FILE") or get_settings().env_file_path or "/etc/srblogs/backend.env"
    return Path(raw)


def is_installed() -> bool:
    return install_lock_path().exists()


def ensure_base_data_dirs() -> None:
    base = data_path()
    for relative in (
        "",
        "posts",
        "moments",
        "chatters",
        "comments",
        "photos",
        "uploads",
        "audit",
        ".manual_backups",
        "update_logs",
    ):
        (base / relative).mkdir(parents=True, exist_ok=True)


def ensure_base_data_files() -> None:
    base = data_path()
    defaults: dict[str, Any] = {
        "friends.json": [],
        "projects.json": [],
        "music.json": [],
        "photos/photos.json": [],
    }
    for relative, default in defaults.items():
        path = base / relative
        if not path.exists():
            safe_write_json(path, default, make_backup=False)


def site_start_time_from_settings(settings_data: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    if settings.site_start_time.strip():
        return settings.site_start_time.strip()
    data = settings_data if isinstance(settings_data, dict) else safe_read_json(data_path() / "settings.json", {})
    value = str(data.get("siteStartTime") or data.get("buildDate") or "").strip() if isinstance(data, dict) else ""
    return value


def missing_items() -> list[str]:
    base = data_path()
    items: list[str] = []
    if not install_lock_path().exists():
        items.append("installLock")
    if not env_path().exists():
        items.append("backendEnv")
    settings_path = base / "settings.json"
    if not settings_path.exists():
        items.append("settings")
    settings_data = safe_read_json(settings_path, {}) if settings_path.exists() else {}
    if not site_start_time_from_settings(settings_data):
        items.append("siteStartTime")
    for relative in ("posts", "moments", "chatters", "uploads", "photos"):
        if not (base / relative).exists():
            items.append(relative)
    return items


def install_status() -> dict[str, Any]:
    installed = is_installed()
    return {
        "installed": installed,
        "needsInstall": not installed,
        "missingItems": [] if installed else missing_items(),
    }


def register_failed_attempt(ip: str) -> None:
    now = time.time()
    attempts = [stamp for stamp in _failed_attempts.get(ip, []) if now - stamp < FAIL_WINDOW_SECONDS]
    attempts.append(now)
    _failed_attempts[ip] = attempts


def check_rate_limit(ip: str) -> None:
    now = time.time()
    attempts = [stamp for stamp in _failed_attempts.get(ip, []) if now - stamp < FAIL_WINDOW_SECONDS]
    _failed_attempts[ip] = attempts
    if len(attempts) >= MAX_FAILED_ATTEMPTS:
        raise InstallRateLimitError("安装尝试过于频繁，请稍后再试。")


def clear_failed_attempts(ip: str) -> None:
    _failed_attempts.pop(ip, None)


def validate_password(username: str, password: str) -> None:
    text = (password or "").strip()
    user = (username or "").strip().lower()
    lowered = text.lower()
    if len(text) < 12:
        raise InstallError("管理员密码至少需要 12 位。")
    if lowered in WEAK_PASSWORDS or lowered == user:
        raise InstallError("管理员密码过弱，请更换更安全的密码。")
    if text.isdigit() or text.isalpha():
        raise InstallError("管理员密码不能是纯数字或纯字母。")
    if not any(ch.isalpha() for ch in text) or not any(ch.isdigit() for ch in text):
        raise InstallError("管理员密码必须同时包含字母和数字。")


def normalize_cors(value: Any, public_base_url: str) -> str:
    if isinstance(value, list):
        items = [str(item).strip().rstrip("/") for item in value if str(item).strip()]
    else:
        items = [item.strip().rstrip("/") for item in str(value or "").split(",") if item.strip()]
    public = public_base_url.strip().rstrip("/")
    if public and public not in items:
        items.insert(0, public)
    return ",".join(dict.fromkeys(items))


def update_process_environment(values: dict[str, str]) -> None:
    for key, value in values.items():
        os.environ[key] = value
    get_settings.cache_clear()


def write_env(values: dict[str, str]) -> Path:
    target = env_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    existing: dict[str, str] = {}
    if target.exists():
        for line in target.read_text(encoding="utf-8").splitlines():
            if not line or line.lstrip().startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            existing[key.strip()] = value.strip()
    if "ADMIN_PASSWORD_HASH" in values:
        existing.pop("ADMIN_PASSWORD", None)
    merged = {**existing, **values}
    ordered_keys = [
        "APP_NAME",
        "APP_ENV",
        "DATA_DIR",
        "PUBLIC_BASE_URL",
        "SITE_START_TIME",
        "ADMIN_USERNAME",
        "ADMIN_PASSWORD_HASH",
        "ADMIN_PASSWORD",
        "JWT_SECRET",
        "JWT_EXPIRE_MINUTES",
        "CORS_ORIGINS",
        "UPLOAD_DRIVER",
        "UPLOAD_MAX_SIZE",
        "UPLOAD_ALLOWED_TYPES",
    ]
    def env_line(key: str, value: str) -> str:
        escaped = str(value).replace("'", "'\"'\"'")
        return f"{key}='{escaped}'"

    lines = ["# Generated by SRBlogs installer. Keep this file on the server only."]
    for key in ordered_keys:
        if key in merged:
            lines.append(env_line(key, merged[key]))
    for key in sorted(k for k in merged if k not in ordered_keys):
        lines.append(env_line(key, merged[key]))
    safe_write_text(target, "\n".join(lines) + "\n", make_backup=True)
    try:
        os.chmod(target, 0o600)
    except OSError:
        pass
    return target


def merge_settings(payload: dict[str, Any], site_start_time: str) -> dict[str, Any]:
    path = data_path() / "settings.json"
    current = safe_read_json(path, {})
    data = current if isinstance(current, dict) else {}
    data.setdefault("siteTitle", payload["siteTitle"])
    data.setdefault("title", payload["siteTitle"])
    data.setdefault("author", payload["author"])
    data.setdefault("authorName", payload["author"])
    data.setdefault("description", "")
    data.setdefault("subtitle", "")
    data.setdefault("socialLinks", {})
    data.setdefault("bgImages", [])
    data.setdefault("cloudMusicIds", [])
    data["siteStartTime"] = data.get("siteStartTime") or site_start_time
    data["buildDate"] = data.get("buildDate") or site_start_time
    safe_write_json(path, data, make_backup=True)
    return data


def create_install_lock(site_start_time: str) -> None:
    lock = {
        "installed": True,
        "installedAt": now_iso(),
        "version": INSTALL_VERSION,
        "siteStartTime": site_start_time,
    }
    safe_write_json(install_lock_path(), lock, make_backup=False)


def install(payload: dict[str, Any]) -> dict[str, Any]:
    if is_installed():
        raise InstallError("SRBlogs 已完成安装，不能重复初始化。")
    ensure_base_data_dirs()
    ensure_base_data_files()
    site_start_time = str(payload.get("siteStartTime") or "").strip() or now_iso()
    public_base_url = str(payload.get("publicBaseUrl") or "").strip().rstrip("/") or "http://127.0.0.1:8000"
    admin_username = str(payload.get("adminUsername") or "").strip() or "admin"
    admin_password = str(payload.get("adminPassword") or "")
    validate_password(admin_username, admin_password)
    admin_password_hash = hash_admin_password(admin_password)
    cors_origins = normalize_cors(payload.get("corsOrigins"), public_base_url)
    jwt_secret = secrets.token_urlsafe(48)
    env_values = {
        "APP_NAME": "SRBlogs API",
        "APP_ENV": "production",
        "DATA_DIR": str(data_path()),
        "PUBLIC_BASE_URL": public_base_url,
        "SITE_START_TIME": site_start_time,
        "ADMIN_USERNAME": admin_username,
        "ADMIN_PASSWORD_HASH": admin_password_hash,
        "JWT_SECRET": jwt_secret,
        "JWT_EXPIRE_MINUTES": "1440",
        "CORS_ORIGINS": cors_origins,
        "UPLOAD_DRIVER": "local",
        "UPLOAD_MAX_SIZE": str(get_settings().upload_max_size),
        "UPLOAD_ALLOWED_TYPES": get_settings().upload_allowed_types,
    }
    write_env(env_values)
    merge_settings({
        "siteTitle": str(payload.get("siteTitle") or "SRBlogs").strip() or "SRBlogs",
        "author": str(payload.get("author") or admin_username).strip() or admin_username,
    }, site_start_time)
    create_install_lock(site_start_time)
    update_process_environment(env_values)
    return {
        "ok": True,
        "installed": True,
        "restartRequired": True,
        "siteStartTime": site_start_time,
        "loginUrl": "/admin/login",
    }
