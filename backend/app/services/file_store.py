from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import get_settings

SLUG_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,80}$")


class FileStoreError(ValueError):
    pass


def _data_root() -> Path:
    root = get_settings().data_path.resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def validate_slug(slug: str) -> str:
    value = slug.strip()
    if not value or ".." in value or "/" in value or "\\" in value:
        raise FileStoreError("Invalid slug")
    if not SLUG_RE.match(value):
        raise FileStoreError("Slug may only contain letters, numbers, underscores and hyphens, and must be 1-81 characters.")
    return value


def resolve_data_path(*parts: str | Path, must_exist: bool = False) -> Path:
    root = _data_root()
    target = root.joinpath(*[str(part) for part in parts]).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise FileStoreError("Resolved path escapes data directory.") from exc
    if must_exist and not target.exists():
        raise FileNotFoundError(str(target))
    return target


def backup_file(path: Path) -> Path | None:
    if not path.exists():
        return None
    backup_dir = path.parent / ".backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    backup_path = backup_dir / f"{path.name}.{stamp}.bak"
    shutil.copy2(path, backup_path)
    return backup_path


def safe_read_text(path: Path, default: str = "") -> str:
    if not path.exists():
        return default
    return path.read_text(encoding="utf-8")


def safe_write_text(path: Path, content: str, *, make_backup: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if make_backup:
        backup_file(path)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def safe_read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(safe_read_text(path))
    except Exception:
        return default


def safe_write_json(path: Path, data: Any, *, make_backup: bool = True) -> None:
    safe_write_text(path, json.dumps(data, ensure_ascii=False, indent=2), make_backup=make_backup)
