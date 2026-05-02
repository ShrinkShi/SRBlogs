from __future__ import annotations

import os
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

from app.services.file_store import FileStoreError, resolve_data_path

BACKUP_DIR_NAME = ".manual_backups"
BACKUP_NAME_REPLACEMENTS = ("/", "\\", "..")
INCLUDED_PATHS = (
    "posts",
    "moments",
    "chatters",
    "comments",
    "photos",
    "friends.json",
    "projects.json",
    "music.json",
    "settings.json",
    "about.md",
    "uploads",
)
EXCLUDED_NAMES = {".env", ".venv", "node_modules", "dist", BACKUP_DIR_NAME}
SECRET_KEYS = ("secret", "password", "token", "key", "authorization")


class BackupError(ValueError):
    pass


def manual_backup_dir() -> Path:
    path = resolve_data_path(BACKUP_DIR_NAME)
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_backup_name(name: str) -> str:
    value = name.strip()
    if not value.endswith(".zip") or any(token in value for token in BACKUP_NAME_REPLACEMENTS):
        raise BackupError("Invalid backup name")
    path = (manual_backup_dir() / value).resolve()
    try:
        path.relative_to(manual_backup_dir().resolve())
    except ValueError as exc:
        raise BackupError("Backup path escapes backup directory") from exc
    return value


def _timestamp(prefix: str = "") -> str:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}{stamp}.zip"


def _should_skip(path: Path) -> bool:
    return any(part in EXCLUDED_NAMES for part in path.parts) or path.name == ".env"


def _iter_backup_files(root: Path):
    for rel in INCLUDED_PATHS:
        path = resolve_data_path(rel)
        if not path.exists() or _should_skip(path):
            continue
        if path.is_file():
            yield path, path.relative_to(root)
            continue
        for file in path.rglob("*"):
            if file.is_file() and not _should_skip(file.relative_to(root)):
                yield file, file.relative_to(root)


def _sanitize_value(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            if any(token in str(key).lower() for token in SECRET_KEYS):
                continue
            cleaned[key] = _sanitize_value(item)
        return cleaned
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    return value


def _write_backup_member(archive: zipfile.ZipFile, file: Path, rel: Path) -> None:
    if rel.as_posix() == "settings.json":
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
            archive.writestr(rel.as_posix(), json.dumps(_sanitize_value(data), ensure_ascii=False, indent=2))
            return
        except Exception:
            pass
    archive.write(file, rel.as_posix())


def create_backup(*, prefix: str = "") -> dict:
    root = resolve_data_path()
    backup_dir = manual_backup_dir()
    name = _timestamp(prefix)
    target = backup_dir / name
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file, rel in _iter_backup_files(root):
            _write_backup_member(archive, file, rel)
    stat = target.stat()
    return {
        "name": name,
        "createdAt": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
        "size": stat.st_size,
    }


def list_backups() -> list[dict]:
    items: list[dict] = []
    for file in sorted(manual_backup_dir().glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True):
        stat = file.stat()
        items.append({
            "name": file.name,
            "createdAt": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            "size": stat.st_size,
        })
    return items


def backup_path(name: str) -> Path:
    safe_name = validate_backup_name(name)
    path = manual_backup_dir() / safe_name
    if not path.exists():
        raise FileNotFoundError(safe_name)
    return path


def _safe_zip_members(zip_path: Path) -> list[zipfile.ZipInfo]:
    root = resolve_data_path().resolve()
    members: list[zipfile.ZipInfo] = []
    with zipfile.ZipFile(zip_path, "r") as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            member_path = Path(member.filename)
            if member_path.is_absolute() or any(part in ("", ".", "..") for part in member_path.parts):
                raise BackupError("Backup zip contains unsafe path")
            if _should_skip(member_path):
                raise BackupError("Backup zip contains excluded path")
            target = root.joinpath(member_path).resolve()
            try:
                target.relative_to(root)
            except ValueError as exc:
                raise BackupError("Backup zip escapes data directory") from exc
            if member_path.parts[0] not in {Path(path).parts[0] for path in INCLUDED_PATHS}:
                raise BackupError("Backup zip contains unsupported path")
            members.append(member)
    return members


def _clear_restore_scope() -> None:
    for rel in INCLUDED_PATHS:
        path = resolve_data_path(rel)
        if not path.exists():
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def _write_member(archive: zipfile.ZipFile, member: zipfile.ZipInfo, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f".{target.name}.{os.getpid()}.restore.tmp")
    with archive.open(member, "r") as src, tmp.open("wb") as dst:
        shutil.copyfileobj(src, dst)
    os.replace(tmp, target)


def restore_backup(name: str) -> dict:
    path = backup_path(name)
    members = _safe_zip_members(path)
    pre_restore = create_backup(prefix="pre-restore-")
    root = resolve_data_path().resolve()
    _clear_restore_scope()
    with zipfile.ZipFile(path, "r") as archive:
        for member in members:
            target = root.joinpath(member.filename).resolve()
            _write_member(archive, member, target)
    return {"ok": True, "restored": name, "preRestoreBackup": pre_restore["name"]}


def import_backup(file: BinaryIO) -> dict:
    name = _timestamp("import-")
    target = manual_backup_dir() / name
    with target.open("wb") as handle:
        shutil.copyfileobj(file, handle)
    try:
        return restore_backup(name)
    except Exception:
        target.unlink(missing_ok=True)
        raise
