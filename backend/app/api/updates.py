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

from fastapi import APIRouter, Depends, HTTPException, Query, Request
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
        "errorCode": "",
        "message": "",
    },
}

STALE_TASK_MESSAGE = "更新进程已经退出，任务状态已自动修复。"
SUDO_PASSWORD_REQUIRED_MESSAGE = "当前服务器未配置免密码 sudo，无法通过 WebUI 一键更新。"
UPDATER_STATE_DIR = Path(os.getenv("SRBLOGS_UPDATER_STATE_DIR", "/var/lib/srblogs/update"))
UPDATER_SERVICE = os.getenv("SRBLOGS_UPDATER_SERVICE", "srblogs-updater.service")
UPDATER_BINARY = Path(os.getenv("SRBLOGS_UPDATER_BINARY", "/usr/local/sbin/srblogs-update"))
UPDATER_STATUS_FILE = UPDATER_STATE_DIR / "status.json"
UPDATER_REQUEST_FILE = UPDATER_STATE_DIR / "request.json"
UPDATER_DEFAULT_LOG = UPDATER_STATE_DIR / "updater.log"


class IgnoreRequest(BaseModel):
    tag: str


class RunUpdateRequest(BaseModel):
    tag: str = ""


def _store() -> JsonStore:
    return JsonStore(get_settings().data_path, "update_state.json", DEFAULT_UPDATE_STATE)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _default_update_task() -> dict[str, Any]:
    return {
        "taskId": "",
        "status": "idle",
        "startedAt": "",
        "finishedAt": "",
        "pid": None,
        "exitCode": None,
        "currentStep": "idle",
        "progress": 0,
        "logPath": "",
        "exitPath": "",
        "lastLines": [],
        "updatedAt": "",
        "lastLogAt": "",
        "errorCode": "",
        "errorMessage": "",
        "tag": "",
    }


def _default_updater_status() -> dict[str, Any]:
    return {
        "taskId": "",
        "status": "idle",
        "startedAt": "",
        "finishedAt": "",
        "updatedAt": "",
        "pid": None,
        "exitCode": None,
        "currentStep": "idle",
        "progress": 0,
        "logPath": str(UPDATER_DEFAULT_LOG),
        "lastLines": [],
        "errorCode": "",
        "errorMessage": "",
        "message": "",
        "repo": GITHUB_REPO,
        "targetVersion": "",
        "previousVersion": "",
        "rollback": False,
    }


def _read_json_file(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return dict(fallback)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return dict(fallback)
    if not isinstance(payload, dict):
        return dict(fallback)
    merged = dict(fallback)
    merged.update(payload)
    return merged


def _read_updater_status(lines: int = 100) -> dict[str, Any]:
    status = _read_json_file(UPDATER_STATUS_FILE, _default_updater_status())
    log_path = str(status.get("logPath") or UPDATER_DEFAULT_LOG)
    status["lastLines"] = _tail_lines(log_path, lines)
    status["lastLogAt"] = _log_mtime(log_path)
    if status.get("status") == "running" and status.get("pid") and not _pid_is_alive(status.get("pid")):
        status.update({
            "status": "failed",
            "finishedAt": status.get("finishedAt") or _now(),
            "updatedAt": _now(),
            "exitCode": status.get("exitCode") if status.get("exitCode") is not None else -1,
            "errorCode": "stale_task",
            "errorMessage": STALE_TASK_MESSAGE,
            "message": STALE_TASK_MESSAGE,
        })
    return status


def _updater_status_to_task(status: dict[str, Any]) -> dict[str, Any]:
    return {
        "taskId": status.get("taskId") or "",
        "status": status.get("status") or "idle",
        "startedAt": status.get("startedAt") or "",
        "finishedAt": status.get("finishedAt") or "",
        "pid": status.get("pid"),
        "exitCode": status.get("exitCode"),
        "currentStep": status.get("currentStep") or "idle",
        "progress": max(0, min(100, int(status.get("progress") or 0))),
        "logPath": status.get("logPath") or str(UPDATER_DEFAULT_LOG),
        "lastLines": status.get("lastLines") or [],
        "updatedAt": status.get("updatedAt") or status.get("lastLogAt") or "",
        "lastLogAt": status.get("lastLogAt") or "",
        "errorCode": status.get("errorCode") or "",
        "errorMessage": status.get("errorMessage") or status.get("message") or "",
        "tag": status.get("targetVersion") or "",
    }


def _systemctl_path() -> str:
    return shutil.which("systemctl") or "systemctl"


def _sudo_path() -> str:
    return shutil.which("sudo") or "sudo"


def _systemctl_command(action: str) -> list[str]:
    command = [_systemctl_path(), action, UPDATER_SERVICE]
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        return command
    return [_sudo_path(), "-n", *command]


def _check_fixed_systemctl(action: str, debug_logs: list[str]) -> tuple[bool, str, str]:
    command = _systemctl_command(action)
    debug_logs.append(f"固定 systemctl 命令: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=8,
            check=False,
        )
    except FileNotFoundError as exc:
        debug_logs.append(f"systemctl/sudo 不存在: {exc}")
        return False, "unsupported_platform", "当前环境缺少 systemd 或 sudo，无法使用一键更新。"
    except subprocess.TimeoutExpired:
        debug_logs.append("systemctl 权限检查超时")
        return False, "updater_status_timeout", "检查 updater service 状态超时。"
    except Exception as exc:
        debug_logs.append(f"systemctl 权限检查异常: {exc}")
        return False, "unknown_error", str(exc)
    if result.returncode == 0:
        return True, "", ""
    stderr = (result.stderr or result.stdout or "").strip()
    debug_logs.append(f"systemctl {action} exitCode: {result.returncode}")
    if stderr:
        debug_logs.append(f"systemctl {action} output: {stderr[:500]}")
    if "password is required" in stderr.lower() or "a password is required" in stderr.lower():
        return False, "sudo_password_required", "当前服务器未配置 srblogs 用户免密码启动 updater service。"
    if "not found" in stderr.lower() or "could not be found" in stderr.lower() or "not-loaded" in stderr.lower():
        return False, "updater_service_missing", "未安装 srblogs-updater.service，请先执行 deploy/install-updater.sh。"
    return False, "updater_service_unavailable", stderr or "updater service 不可用。"


def _write_updater_request(tag: str, actor: str) -> None:
    payload = {
        "repo": GITHUB_REPO,
        "targetVersion": tag,
        "requestedAt": _now(),
        "requestedBy": actor,
    }
    UPDATER_REQUEST_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _tail_lines(path: str | Path, lines: int = 100) -> list[str]:
    target = Path(path)
    if not target.exists() or not target.is_file():
        return []
    count = max(1, min(lines, 500))
    try:
        return target.read_text(encoding="utf-8", errors="ignore").splitlines()[-count:]
    except Exception:
        return []


def _log_mtime(path: str | Path) -> str:
    target = Path(path)
    if not target.exists() or not target.is_file():
        return ""
    try:
        return datetime.fromtimestamp(target.stat().st_mtime).isoformat(timespec="seconds")
    except Exception:
        return ""


def _pid_is_alive(pid: Any) -> bool:
    try:
        value = int(pid)
    except (TypeError, ValueError):
        return False
    if value <= 0:
        return False
    try:
        os.kill(value, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except ValueError:
        return False
    except OSError:
        return False
    return True


def _task_to_run(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": task.get("status") or "idle",
        "pid": task.get("pid"),
        "tag": task.get("tag") or "",
        "startedAt": task.get("startedAt") or "",
        "finishedAt": task.get("finishedAt") or "",
        "log": task.get("logPath") or "",
        "taskId": task.get("taskId") or "",
        "exitCode": task.get("exitCode"),
        "errorCode": task.get("errorCode") or "",
        "message": task.get("errorMessage") or "",
    }


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
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "SRBlogs-Update-Checker",
    }
    token = os.getenv("SRBLOGS_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(
        url,
        headers=headers,
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
        with urllib.request.urlopen(_github_request(url), timeout=6) as response:
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


def _runtime_support(script: Path, debug_logs: list[str]) -> tuple[bool, str, str]:
    system = platform.system()
    is_linux = system.lower() == "linux"
    debug_logs.append(f"运行系统: {system}")
    debug_logs.append(f"是否 Linux 环境: {is_linux}")
    debug_logs.append(f"updater binary: {UPDATER_BINARY}")
    debug_logs.append(f"updater service: {UPDATER_SERVICE}")
    debug_logs.append(f"updater status: {UPDATER_STATUS_FILE}")
    if system.lower().startswith("win"):
        message = "当前环境不支持一键更新，请在 Linux 服务器执行"
        debug_logs.append(f"一键更新是否支持: False ({message})")
        return False, "unsupported_platform", message
    if not is_linux:
        message = "当前环境不支持一键更新，请在 Linux systemd 服务器执行。"
        debug_logs.append(f"一键更新是否支持: False ({message})")
        return False, "unsupported_platform", message
    if not UPDATER_BINARY.exists():
        message = "未安装受限 updater，请先执行 deploy/install-updater.sh。"
        debug_logs.append(f"一键更新是否支持: False ({message})")
        return False, "updater_service_missing", message
    if not UPDATER_STATUS_FILE.exists():
        message = "未找到 updater 状态文件，请先执行 deploy/install-updater.sh。"
        debug_logs.append(f"一键更新是否支持: False ({message})")
        return False, "updater_service_missing", message
    if not get_settings().srblogs_update_enabled:
        message = "后端一键更新已禁用，请设置 SRBLOGS_UPDATE_ENABLED=true。"
        debug_logs.append(f"一键更新是否支持: False ({message})")
        return False, "unsupported_platform", message
    if not shutil.which("systemctl"):
        message = "当前环境没有 systemctl，无法使用 updater service。"
        debug_logs.append(f"一键更新是否支持: False ({message})")
        return False, "unsupported_platform", message
    if hasattr(os, "geteuid") and os.geteuid() != 0 and not shutil.which("sudo"):
        message = "当前后端进程不是 root，且未找到 sudo，无法启动 updater service。"
        debug_logs.append(f"一键更新是否支持: False ({message})")
        return False, "unsupported_platform", message
    ok, code, message = _check_fixed_systemctl("status", debug_logs)
    if not ok and code not in {"updater_service_unavailable"}:
        return False, code, message
    debug_logs.append("一键更新是否支持: True")
    return True, "", ""


def _make_status(state: dict[str, Any], debug_logs: list[str] | None = None, prefer_run_status: bool = False) -> dict[str, Any]:
    logs = list(debug_logs or [])
    settings = get_settings()
    repo = settings.srblogs_update_repo.strip() or GITHUB_REPO
    current, version_error_code, version_error_message = _current_version(logs)
    latest = state.get("latest") or {}
    latest_tag = str(latest.get("tag") or "")
    ignored_tag = str(state.get("ignoredTag") or "")
    has_update = _is_newer(latest_tag, current["version"]) and latest_tag != ignored_tag
    task = _updater_status_to_task(_read_updater_status())
    if task.get("status") and task.get("status") != "idle":
        run_state = _task_to_run(task)
    else:
        run_state = state.get("run") or DEFAULT_UPDATE_STATE["run"]
        if prefer_run_status and str(run_state.get("status") or "") == "running":
            task.update(
                {
                    "status": "running",
                    "startedAt": run_state.get("startedAt") or "",
                    "currentStep": "queued",
                    "progress": 1,
                    "tag": run_state.get("tag") or "",
                    "updatedAt": _now(),
                    "errorCode": "",
                    "errorMessage": "",
                }
            )
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
    script = UPDATER_BINARY
    supported, update_error_code, update_error_message = _runtime_support(script, logs)
    message = str(detection_error_message or update_error_message or "")
    if prefer_run_status and update_error_code == "sudo_password_required":
        status = "failed"
        message = update_error_message
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
        "task": task,
        "debugLogs": logs,
        # Compatibility fields for older admin builds.
        "current": current,
        "latest": latest,
        "ignoredTag": ignored_tag,
        "updateAvailable": has_update,
        "updateConfigured": supported,
    }


def _refresh_latest_release(state: dict[str, Any], debug_logs: list[str]) -> dict[str, Any]:
    previous_latest = state.get("latest") or {}
    latest = _fetch_latest_release(get_settings().srblogs_update_repo, debug_logs)
    if latest.get("error") and previous_latest.get("tag"):
        debug_logs.append("GitHub release check failed; keeping last successful release metadata.")
        latest = {
            **previous_latest,
            "error": latest.get("error") or "",
            "errorType": latest.get("errorType") or "",
            "errorCode": latest.get("errorCode") or "",
        }
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


@router.get("/admin/update/task")
@router.get("/admin/updates/task")
def update_task():
    return _updater_status_to_task(_read_updater_status())


@router.get("/admin/update/logs")
@router.get("/admin/updates/logs")
def update_logs(lines: int = Query(100, ge=1, le=500)):
    task = _updater_status_to_task(_read_updater_status(lines))
    log_path = str(task.get("logPath") or "")
    return {
        "taskId": task.get("taskId") or "",
        "status": task.get("status") or "idle",
        "logPath": log_path,
        "lines": _tail_lines(log_path, lines),
    }


@router.get("/admin/update/progress")
@router.get("/admin/updates/progress")
def update_progress(lines: int = Query(100, ge=1, le=500)):
    task = _updater_status_to_task(_read_updater_status(lines))
    log_path = str(task.get("logPath") or "")
    last_lines = task.get("lastLines") or _tail_lines(log_path, lines)
    current_step = str(task.get("currentStep") or "idle")
    progress = max(0, min(100, int(task.get("progress") or 0)))
    return {
        "taskId": task.get("taskId") or "",
        "status": task.get("status") or "idle",
        "currentStep": current_step,
        "progress": progress,
        "lastLines": last_lines,
        "startedAt": task.get("startedAt") or "",
        "finishedAt": task.get("finishedAt") or "",
        "updatedAt": task.get("updatedAt") or task.get("lastLogAt") or task.get("finishedAt") or task.get("startedAt") or "",
        "lastLogAt": task.get("lastLogAt") or _log_mtime(log_path),
        "pid": task.get("pid"),
        "exitCode": task.get("exitCode"),
        "errorCode": task.get("errorCode") or "",
        "errorMessage": task.get("errorMessage") or "",
        "logPath": log_path,
    }


@router.post("/admin/update/start")
@router.post("/admin/updates/start")
@router.post("/admin/update/run")
@router.post("/admin/updates/run")
def start_update(payload: RunUpdateRequest, request: Request, actor: str = Depends(require_admin)):
    store = _store()
    debug_logs: list[str] = []
    state = store.read()
    supported, support_code, reason = _runtime_support(UPDATER_BINARY, debug_logs)
    if not supported:
        run_status = "failed" if support_code == "sudo_password_required" else (support_code or "unsupported_platform")
        state["run"] = {
            **DEFAULT_UPDATE_STATE["run"],
            "status": run_status,
            "tag": payload.tag,
            "errorCode": support_code,
            "message": reason,
        }
        store.write(state)
        return _make_status(state, debug_logs, prefer_run_status=True)

    existing_task = _updater_status_to_task(_read_updater_status())
    if existing_task.get("status") == "running":
        state["run"] = _task_to_run(existing_task)
        store.write(state)
        return _make_status(state, debug_logs, prefer_run_status=True)

    state = _refresh_latest_release(state, debug_logs)
    latest = state.get("latest") or {}

    run_state = state.get("run") or {}
    if run_state.get("status") == "running":
        task = _updater_status_to_task(_read_updater_status())
        if task.get("status") == "running":
            state["run"] = _task_to_run(task)
            store.write(state)
            return _make_status(state, debug_logs, prefer_run_status=True)
    if latest.get("error"):
        raise HTTPException(status_code=502, detail=str(latest.get("error")))

    tag = payload.tag.strip() or str(latest.get("tag") or "")
    if not tag:
        raise HTTPException(status_code=400, detail="未检测到可更新的 GitHub Release")

    try:
        _write_updater_request(tag, actor)
    except Exception as exc:
        debug_logs.append(f"写入 updater request 失败: {exc}")
        state["run"] = {
            **DEFAULT_UPDATE_STATE["run"],
            "status": "failed",
            "tag": tag,
            "errorCode": "updater_request_write_failed",
            "message": "无法写入 updater 请求文件，请检查 /var/lib/srblogs/update/request.json 权限。",
        }
        store.write(state)
        write_audit(actor=actor, action="updates.start", resource="system", result="failed", message=str(exc))
        return _make_status(state, debug_logs, prefer_run_status=True)

    ok, code, message = _check_fixed_systemctl("start", debug_logs)
    if not ok:
        state["run"] = {
            **DEFAULT_UPDATE_STATE["run"],
            "status": "failed",
            "tag": tag,
            "errorCode": code,
            "message": message,
        }
        store.write(state)
        write_audit(actor=actor, action="updates.start", resource="system", result="failed", message=message)
        return _make_status(state, debug_logs, prefer_run_status=True)

    task = _updater_status_to_task(_read_updater_status())
    if task.get("status") == "idle":
        task.update({
            "status": "running",
            "currentStep": "queued",
            "progress": 1,
            "tag": tag,
            "updatedAt": _now(),
            "errorMessage": "",
        })
    state["run"] = _task_to_run(task)
    state["run"]["message"] = "受限 updater 已启动，可在版本弹窗查看状态。"
    store.write(state)
    write_audit(
        actor=actor,
        action="updates.start",
        resource="system",
        target=tag,
        result="success",
        message="Started srblogs-updater.service",
        ip=request.client.host if request.client else "",
        detail={"service": UPDATER_SERVICE, "request": str(UPDATER_REQUEST_FILE)},
    )
    return _make_status(state, debug_logs, prefer_run_status=True)
