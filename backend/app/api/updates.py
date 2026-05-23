from __future__ import annotations

import json
import os
import platform
import shutil
import socket
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
from app import version as version_info
from app.version import GITHUB_REPO


router = APIRouter(tags=["admin-update"], dependencies=[Depends(require_admin)])

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
        "message": "",
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


def _current_version(debug_logs: list[str]) -> tuple[dict[str, str], str, str]:
    source = Path(getattr(version_info, "__file__", "backend/app/version.py")).resolve()
    debug_logs.append(f"读取当前版本来源: {source}")
    try:
        version = str(getattr(version_info, "APP_VERSION", "")).strip()
    except Exception as exc:
        debug_logs.append(f"读取版本常量失败: {exc}")
        return (
            {"version": "unknown", "source": str(source)},
            "version_constant_missing",
            f"本地版本常量读取失败：{exc}",
        )
    if not version:
        debug_logs.append("APP_VERSION 为空或不存在")
        return (
            {"version": "unknown", "source": str(source)},
            "version_constant_missing",
            "本地版本常量 APP_VERSION 缺失。",
        )
    debug_logs.append(f"当前版本: {version}")
    return {"version": version, "source": str(source)}, "", ""


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


def _github_request(url: str) -> urllib.request.Request:
    return urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "SRBlogs-Update-Checker",
        },
    )


def _release_error(message: str, error_code: str) -> dict[str, str]:
    return {"error": message, "errorType": error_code, "errorCode": error_code}


def _http_error_body(exc: urllib.error.HTTPError) -> str:
    try:
        return exc.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def _is_rate_limited(exc: urllib.error.HTTPError, body: str) -> bool:
    remaining = exc.headers.get("X-RateLimit-Remaining", "")
    return exc.code in {403, 429} and (remaining == "0" or "rate limit" in body.lower())


def _fetch_latest_release(repo: str, debug_logs: list[str]) -> dict[str, Any]:
    target_repo = repo.strip() or GITHUB_REPO
    url = f"https://api.github.com/repos/{target_repo}/releases/latest"
    debug_logs.append(f"GitHub repo: {target_repo}")
    debug_logs.append(f"GitHub API URL: {url}")
    try:
        with urllib.request.urlopen(_github_request(url), timeout=10) as response:
            debug_logs.append(f"GitHub HTTP status: {getattr(response, 'status', 200)}")
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = _http_error_body(exc)
        debug_logs.append(f"GitHub HTTP status: {exc.code}")
        if body:
            debug_logs.append(f"GitHub error body: {body[:300]}")
        if exc.code == 404:
            return _release_error("未找到 GitHub Release，请先在 GitHub 创建 release。", "github_release_not_found")
        if _is_rate_limited(exc, body):
            return _release_error("GitHub API 限流，请稍后再试。", "github_rate_limited")
        return _release_error(f"GitHub Release 查询失败：HTTP {exc.code}", "unknown_error")
    except TimeoutError:
        debug_logs.append("GitHub request timeout")
        return _release_error("访问 GitHub 超时，请检查服务器网络后重试。", "github_timeout")
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, (TimeoutError, socket.timeout)):
            debug_logs.append(f"GitHub request timeout: {exc.reason}")
            return _release_error("访问 GitHub 超时，请检查服务器网络后重试。", "github_timeout")
        debug_logs.append(f"GitHub network error: {exc.reason}")
        return _release_error("网络不可达，无法访问 GitHub Releases。", "github_network_error")
    except socket.timeout:
        debug_logs.append("GitHub request socket timeout")
        return _release_error("访问 GitHub 超时，请检查服务器网络后重试。", "github_timeout")
    except OSError:
        debug_logs.append("GitHub request network OSError")
        return _release_error("网络不可达，无法访问 GitHub Releases。", "github_network_error")
    except Exception as exc:
        debug_logs.append(f"GitHub unknown error: {exc}")
        return _release_error(f"GitHub Release 查询失败：{exc}", "unknown_error")

    tag = str(payload.get("tag_name") or "")
    return {
        "tag": tag,
        "name": str(payload.get("name") or tag),
        "url": str(payload.get("html_url") or ""),
        "publishedAt": str(payload.get("published_at") or ""),
        "body": str(payload.get("body") or "")[:4000],
        "zipballUrl": str(payload.get("zipball_url") or ""),
        "error": "",
        "errorType": "",
        "errorCode": "",
    }


def _download_release_zip(url: str, tag: str) -> Path:
    if not url:
        raise RuntimeError("GitHub Release 未返回可下载的 zipball_url")
    download_dir = get_settings().data_path / "update_downloads"
    download_dir.mkdir(parents=True, exist_ok=True)
    safe_tag = tag.strip().replace("/", "-").replace("\\", "-") or "latest"
    target = download_dir / f"SRBlogs-{safe_tag}.zip"
    with urllib.request.urlopen(_github_request(url), timeout=120) as response:
        with target.open("wb") as output:
            shutil.copyfileobj(response, output)
    return target


def _runtime_support(script: Path, debug_logs: list[str]) -> tuple[bool, str, str]:
    system = platform.system()
    is_linux = system.lower() == "linux"
    debug_logs.append(f"运行系统: {system}")
    debug_logs.append(f"是否 Linux 环境: {is_linux}")
    debug_logs.append(f"更新脚本路径: {script}")
    debug_logs.append(f"更新脚本存在: {script.exists()}")
    if system.lower().startswith("win"):
        message = "当前环境不支持一键更新，请在 Linux 服务器执行"
        debug_logs.append(f"一键更新是否支持: False ({message})")
        return False, "unsupported_platform", message
    if not script.exists():
        message = f"未找到更新脚本：{script}"
        debug_logs.append(f"一键更新是否支持: False ({message})")
        return False, "update_script_missing", message
    if not shutil.which("bash"):
        message = "未找到 bash，无法执行 deploy/update.sh。"
        debug_logs.append(f"一键更新是否支持: False ({message})")
        return False, "unsupported_platform", message
    if not get_settings().srblogs_update_enabled:
        message = "后端一键更新已禁用，请设置 SRBLOGS_UPDATE_ENABLED=true。"
        debug_logs.append(f"一键更新是否支持: False ({message})")
        return False, "unsupported_platform", message
    if hasattr(os, "geteuid") and os.geteuid() != 0 and not shutil.which("sudo"):
        message = "当前后端进程不是 root，且未找到 sudo，无法执行需要系统权限的更新脚本。"
        debug_logs.append(f"一键更新是否支持: False ({message})")
        return False, "unsupported_platform", message
    debug_logs.append("一键更新是否支持: True")
    return True, "", ""


def _update_command(script: Path, zip_path: Path) -> list[str]:
    command = ["bash", str(script), "--zip", str(zip_path), "--app-dir", str(_repo_root())]
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        return ["sudo", "-n", *command]
    return command


def _make_status(state: dict[str, Any], debug_logs: list[str] | None = None, prefer_run_status: bool = False) -> dict[str, Any]:
    logs = list(debug_logs or [])
    settings = get_settings()
    repo = settings.srblogs_update_repo.strip() or GITHUB_REPO
    current, version_error_code, version_error_message = _current_version(logs)
    latest = state.get("latest") or {}
    latest_tag = str(latest.get("tag") or "")
    ignored_tag = str(state.get("ignoredTag") or "")
    has_update = _is_newer(latest_tag, current["version"]) and latest_tag != ignored_tag
    run_state = state.get("run") or DEFAULT_UPDATE_STATE["run"]
    latest_error_code = str(latest.get("errorCode") or latest.get("errorType") or "")
    detection_error_code = version_error_code or latest_error_code
    detection_error_message = version_error_message or str(latest.get("error") or "")
    status = "unknown"
    run_status = str(run_state.get("status") or "")
    if prefer_run_status and run_status in {"running", "unsupported", "unsupported_platform", "update_script_missing", "failed"}:
        status = run_status
    elif detection_error_code:
        status = "error"
    elif latest_tag:
        status = "update_available" if has_update else "latest"
    script = _repo_root() / "deploy" / "update.sh"
    supported, update_error_code, update_error_message = _runtime_support(script, logs)
    message = str(detection_error_message or update_error_message or "")
    if prefer_run_status and run_status in {"running", "unsupported", "unsupported_platform", "update_script_missing", "failed"}:
        message = str(run_state.get("message") or update_error_message or detection_error_message or "")
    return {
        "repo": repo,
        "currentVersion": current["version"],
        "latestVersion": latest_tag,
        "hasUpdate": has_update,
        "releaseUrl": str(latest.get("url") or ""),
        "publishedAt": str(latest.get("publishedAt") or ""),
        "notes": str(latest.get("body") or ""),
        "status": status,
        "errorCode": detection_error_code,
        "errorMessage": detection_error_message,
        "platform": platform.system(),
        "message": message,
        "lastCheckedAt": state.get("lastCheckedAt") or "",
        "updateSupported": supported,
        "updateErrorCode": update_error_code,
        "updateErrorMessage": update_error_message,
        "updateEnabled": settings.srblogs_update_enabled,
        "run": run_state,
        "debugLogs": logs,
        # Compatibility fields for older admin builds.
        "current": current,
        "latest": latest,
        "ignoredTag": ignored_tag,
        "updateAvailable": has_update,
        "updateConfigured": supported,
    }


def _refresh_latest_release(state: dict[str, Any], debug_logs: list[str]) -> dict[str, Any]:
    latest = _fetch_latest_release(get_settings().srblogs_update_repo, debug_logs)
    state["latest"] = latest
    state["lastCheckedAt"] = datetime.now().isoformat(timespec="seconds")
    _store().write(state)
    return state


@router.get("/admin/update/status")
@router.get("/admin/updates/status")
def update_status():
    debug_logs: list[str] = []
    state = _store().read()
    return _make_status(_refresh_latest_release(state, debug_logs), debug_logs)


@router.post("/admin/update/check")
@router.post("/admin/updates/check")
def check_update(request: Request, actor: str = Depends(require_admin)):
    debug_logs: list[str] = []
    state = _refresh_latest_release(_store().read(), debug_logs)
    latest = state.get("latest") or {}
    write_audit(
        actor=actor,
        action="updates.check",
        resource="system",
        result="failed" if latest.get("error") else "success",
        message=latest.get("error") or "Checked GitHub release",
        ip=request.client.host if request.client else "",
        detail={"repo": get_settings().srblogs_update_repo, "tag": latest.get("tag", "")},
    )
    return _make_status(state, debug_logs)


@router.post("/admin/update/ignore")
@router.post("/admin/updates/ignore")
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


@router.post("/admin/update/run")
@router.post("/admin/updates/run")
def run_update(payload: RunUpdateRequest, request: Request, actor: str = Depends(require_admin)):
    store = _store()
    script = _repo_root() / "deploy" / "update.sh"
    debug_logs: list[str] = []
    state = store.read()
    supported, support_code, reason = _runtime_support(script, debug_logs)
    if not supported:
        state["run"] = {
            **DEFAULT_UPDATE_STATE["run"],
            "status": support_code or "unsupported_platform",
            "tag": payload.tag,
            "message": reason,
        }
        store.write(state)
        return _make_status(state, debug_logs, prefer_run_status=True)

    state = _refresh_latest_release(state, debug_logs)
    latest = state.get("latest") or {}

    run_state = state.get("run") or {}
    if run_state.get("status") == "running":
        raise HTTPException(status_code=409, detail="已有更新任务正在运行")
    if latest.get("error"):
        raise HTTPException(status_code=502, detail=str(latest.get("error")))

    tag = payload.tag.strip() or str(latest.get("tag") or "")
    try:
        zip_path = _download_release_zip(str(latest.get("zipballUrl") or ""), tag)
    except Exception as exc:
        state["run"] = {
            **DEFAULT_UPDATE_STATE["run"],
            "status": "failed",
            "tag": tag,
            "message": f"Release 下载失败：{exc}",
        }
        store.write(state)
        raise HTTPException(status_code=502, detail="Release 下载失败") from exc

    log_dir = get_settings().data_path / "update_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"update-{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
    command = _update_command(script, zip_path)
    try:
        log_handle = log_path.open("a", encoding="utf-8")
        log_handle.write(f"\n[{datetime.now().isoformat(timespec='seconds')}] start update: {tag}\n")
        log_handle.write(f"command: {' '.join(command)}\n")
        process = subprocess.Popen(
            command,
            cwd=str(_repo_root()),
            stdout=log_handle,
            stderr=subprocess.STDOUT,
        )
        log_handle.close()
    except Exception as exc:
        write_audit(actor=actor, action="updates.run", resource="system", result="failed", message=str(exc))
        raise HTTPException(status_code=500, detail="更新脚本启动失败") from exc

    state["run"] = {
        "status": "running",
        "pid": process.pid,
        "tag": tag,
        "startedAt": datetime.now().isoformat(timespec="seconds"),
        "log": str(log_path),
        "message": "更新任务已启动，请查看日志确认结果。",
    }
    store.write(state)
    write_audit(
        actor=actor,
        action="updates.run",
        resource="system",
        target=tag,
        result="success",
        message="Started deploy/update.sh",
        ip=request.client.host if request.client else "",
        detail={"pid": process.pid, "log": str(log_path)},
    )
    return _make_status(state, debug_logs, prefer_run_status=True)
