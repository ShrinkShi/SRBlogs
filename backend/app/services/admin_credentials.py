from __future__ import annotations

from passlib.context import CryptContext

from app.config import Settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_admin_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_admin_password(password: str, settings: Settings) -> bool:
    password_hash = (settings.admin_password_hash or "").strip()
    if password_hash:
        return pwd_context.verify(password, password_hash)

    # Compatibility for older deployments that still have ADMIN_PASSWORD.
    legacy_password = settings.admin_password or ""
    return bool(legacy_password) and password == legacy_password


def admin_password_configured(settings: Settings) -> bool:
    return bool((settings.admin_password_hash or "").strip() or (settings.admin_password or "").strip())
