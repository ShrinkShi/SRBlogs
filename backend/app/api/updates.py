from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.config import get_settings
from app.services.audit_service import write_audit
from app.services.auth_service import require_admin
from app.services.json_service import JsonStore


router = APIRouter(prefix="/admin/updates", tags=["admin-updates"], dependencies=[Depends(require_admin)])

DEFAULT_UPDATE_STATE: dict[str, Any] = {
    "ignoredTag": "",
    "lastCheckedAt": "",
    "latest": {},
    "run": {
        "status": "idle",
        "pid": None,
        "tag": "",
        "startedAt": "",
        "log": "",
    },
}


class IgnoreRequest(BaseModel):
    tag: str


class RunUpdateRequest(BaseModel):
    tag: str = ""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _store() -> JsonStore:
    return JsonStore(get_settings().data_path, "update_state.json", DEFAULT_UPDATE_STATE)


def _read_version_file(path: Path) -> str:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    return value


def _read_package_version(path: Path) -> str:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    return str(payload.get("version") or "").strip()


def _current_version() -> dict[str, str]:
    root = _repo_root()
    candidates = [
        ("VERSION", _read_version_file(root / "VERSION")),
        ("frontend/package.json", _read_package_version(root / "frontend" / "package.json")),
        ("admin/package.json", _read_package_version(root / "admin" / "package.json")),
    ]
    for source, version in candidates:
        if version:
            return {"version": version, "source": source}
    return {"version": "unknown", "source": "unknown"}


def _version_parts(value: str) -> tuple[int, ...]:
    normalized = value.strip().lstrip("vV")
    parts: list[int] = []
    for item in normalized.replace("-", ".").split("."):
        if item.isdigit():
            parts.append(int(item))
        else:
            break
    return tuple(parts)


def _is_newer(latest: str, current: str) -> bool:
    if not latest or current == "unknown":
        return False
    latest_parts = _version_parts(latest)
    current_parts = _version_parts(current)
    if latest_parts and current_parts:
        return latest_parts > current_parts
    return latest.strip().lstrip("vV") != current.strip().lstrip("vV")


def _fetch_latest_release(repo: str) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "SRBlogs-Update-Checker",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"error": "未找到 GitHub Release。请确认仓库已发布 Releases。"}
        return {"error": f"GitHub Release 查询失败：HTTP {exc.code}"}
    except Exception as exc:
        return {"error": f"GitHub Release 查询失败：{exc}"}

    return {
        "tag": str(payload.get("tag_name") or ""),
        "name": str(payload.get("name") or payload.get("tag_name") or ""),
        "url": str(payload.get("html_url") or ""),
        "publishedAt": str(payload.get("published_at") or ""),
        "body": str(payload.get("body") or "")[:1200],
        "error": "",
    }


def _make_status(state: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    current = _current_version()
    latest = state.get("latest") or {}
    latest_tag = str(latest.get("tag") or "")
    ignored_tag = str(state.get("ignoredTag") or "")
    update_available = _is_newer(latest_tag, current["version"]) and latest_tag != ignored_tag
    return {
        "repo": settings.srblogs_update_repo,
        "current": current,
        "latest": latest,
        "ignoredTag": ignored_tag,
        "lastCheckedAt": state.get("lastCheckedAt") or "",
        "updateAvailable": update_available,
        "updateEnabled": settings.srblogs_update_enabled,
        "updateConfigured": bool(settings.srblogs_update_enabled and settings.srblogs_update_command.strip()),
        "run": state.get("run") or DEFAULT_UPDATE_STATE["run"],
    }


@router.get("/status")
def update_status():
    return _make_status(_store().read())


@router.post("/check")
def check_update(request: Request, actor: str = Depends(require_admin)):
    store = _store()
    state = store.read()
    latest = _fetch_latest_release(get_settings().srblogs_update_repo)
    state["latest"] = latest
    state["lastCheckedAt"] = datetime.now().isoformat(timespec="seconds")
    store.write(state)
    write_audit(
        actor=actor,
        action="updates.check",
        resource="system",
        result="failed" if latest.get("error") else "success",
        message=latest.get("error") or "Checked GitHub release",
        ip=request.client.host if request.client else "",
        detail={"repo": get_settings().srblogs_update_repo, "tag": latest.get("tag", "")},
    )
    return _make_status(state)


@router.post("/ignore")
def ignore_update(payload: IgnoreRequest, request: Request, actor: str = Depends(require_admin)):
    tag = payload.tag.strip()
    if not tag:
        raise HTTPException(status_code=400, detail="缺少要忽略的版本号")
    store = _store()
    state = store.read()
    state["ignoredTag"] = tag
    store.write(state)
    write_audit(
        actor=actor,
        action="updates.ignore",
        resource="system",
        target=tag,
        result="success",
        message="Ignored release update",
        ip=request.client.host if request.client else "",
    )
    return _make_status(state)


@router.post("/run")
def run_update(payload: RunUpdateRequest, request: Request, actor: str = Depends(require_admin)):
    settings = get_settings()
    command = settings.srblogs_update_command.strip()
    if not settings.srblogs_update_enabled or not command:
        raise HTTPException(status_code=400, detail="自动更新未配置。请在后端环境变量中设置 SRBLOGS_UPDATE_ENABLED=true 和 SRBLOGS_UPDATE_COMMAND。")

    store = _store()
    state = store.read()
    run_state = state.get("run") or {}
    if run_state.get("status") == "running":
        raise HTTPException(status_code=409, detail="已有更新任务正在运行")

    log_dir = settings.data_path / "update_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "latest_update.log"
    try:
        log_handle = log_path.open("a", encoding="utf-8")
        log_handle.write(f"\n[{datetime.now().isoformat(timespec='seconds')}] start update: {payload.tag or 'latest'}\n")
        process = subprocess.Popen(
            command,
            cwd=str(_repo_root()),
            shell=True,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
        )
        log_handle.close()
    except Exception as exc:
        write_audit(actor=actor, action="updates.run", resource="system", result="failed", message=str(exc))
        raise HTTPException(status_code=500, detail="更新命令启动失败") from exc

    state["run"] = {
        "status": "running",
        "pid": process.pid,
        "tag": payload.tag,
        "startedAt": datetime.now().isoformat(timespec="seconds"),
        "log": str(log_path),
    }
    store.write(state)
    write_audit(
        actor=actor,
        action="updates.run",
        resource="system",
        target=payload.tag,
        result="success",
        message="Started update command",
        ip=request.client.host if request.client else "",
        detail={"pid": process.pid, "log": str(log_path)},
    )
    return _make_status(state)
