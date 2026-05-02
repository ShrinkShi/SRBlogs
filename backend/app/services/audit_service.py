from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import uuid4

from app.services.file_store import resolve_data_path, safe_read_text

SECRET_KEYS = ("secret", "password", "token", "key", "authorization")


def _clean_detail(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            if any(token in str(key).lower() for token in SECRET_KEYS):
                cleaned[str(key)] = "***"
            else:
                cleaned[str(key)] = _clean_detail(item)
        return cleaned
    if isinstance(value, list):
        return [_clean_detail(item) for item in value]
    return value


def write_audit(
    *,
    actor: str = "system",
    action: str,
    resource: str = "",
    target: str = "",
    result: str = "success",
    message: str = "",
    ip: str = "",
    detail: dict[str, Any] | None = None,
) -> None:
    try:
        audit_dir = resolve_data_path("audit")
        audit_dir.mkdir(parents=True, exist_ok=True)
        log_file = audit_dir / "audit.log"
        entry = {
            "id": uuid4().hex,
            "time": datetime.now().isoformat(timespec="seconds"),
            "actor": actor or "system",
            "action": action,
            "resource": resource,
            "target": target,
            "result": result,
            "message": message,
            "ip": ip,
            "detail": _clean_detail(detail or {}),
        }
        with log_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        return


def read_audit_logs(
    *,
    limit: int = 50,
    offset: int = 0,
    action: str = "",
    resource: str = "",
    q: str = "",
) -> dict[str, Any]:
    log_file = resolve_data_path("audit", "audit.log")
    entries: list[dict[str, Any]] = []
    for line in safe_read_text(log_file, "").splitlines():
        try:
            item = json.loads(line)
        except Exception:
            continue
        if action and item.get("action") != action:
            continue
        if resource and item.get("resource") != resource:
            continue
        if q:
            haystack = " ".join(
                str(item.get(key, ""))
                for key in ("actor", "action", "resource", "target", "result", "message")
            ).lower()
            if q.lower() not in haystack:
                continue
        entries.append(item)
    entries.sort(key=lambda item: str(item.get("time", "")), reverse=True)
    safe_limit = max(1, min(limit, 200))
    safe_offset = max(0, offset)
    return {
        "items": entries[safe_offset:safe_offset + safe_limit],
        "total": len(entries),
        "limit": safe_limit,
        "offset": safe_offset,
    }
