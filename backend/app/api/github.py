from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Query

from app.config import get_settings
from app.services.json_service import JsonStore

router = APIRouter(prefix="/github", tags=["github"])
FETCH_TIMEOUT_SECONDS = 4
CACHE_TTL_SECONDS = 6 * 60 * 60


def _compact_number(value: int) -> str:
    return f"{value:,}" if value >= 1000 else str(value)


def _request(url: str) -> urllib.request.Request:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "SRBlogs-GitHub-Summary",
    }
    token = os.getenv("SRBLOGS_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers)


def _error_payload(code: str, message: str, debug_logs: list[str]) -> dict[str, Any]:
    return {
        "ok": False,
        "stats": [],
        "heatmapCells": [],
        "contributionText": "",
        "errorCode": code,
        "errorMessage": message,
        "debugLogs": debug_logs,
    }


def _cache_store(username: str) -> JsonStore:
    safe = "".join(char for char in username.lower() if char.isalnum() or char in {"-", "_"}) or "default"
    return JsonStore(get_settings().data_path, f"cache/github-summary-{safe}.json", {})


def _cached_payload(username: str, debug_logs: list[str], *, allow_stale: bool = False) -> dict[str, Any] | None:
    cached = _cache_store(username).read()
    if not isinstance(cached, dict):
        return None
    payload = cached.get("payload")
    cached_at = str(cached.get("cachedAt") or "")
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        return None
    try:
        age = datetime.now(timezone.utc).timestamp() - datetime.fromisoformat(cached_at).timestamp()
    except ValueError:
        age = CACHE_TTL_SECONDS + 1
    if not allow_stale and age > CACHE_TTL_SECONDS:
        debug_logs.append(f"GitHub cache expired: age={int(age)}s")
        return None
    next_payload = dict(payload)
    next_logs = list(next_payload.get("debugLogs") or [])
    next_logs.extend(debug_logs)
    next_logs.append(f"GitHub summary served from {'stale ' if age > CACHE_TTL_SECONDS else ''}cache.")
    next_payload["debugLogs"] = next_logs
    next_payload["fromCache"] = True
    next_payload["errorCode"] = ""
    next_payload["errorMessage"] = ""
    return next_payload


def _write_cache(username: str, payload: dict[str, Any]) -> None:
    cache_payload = dict(payload)
    cache_payload["debugLogs"] = []
    _cache_store(username).write({
        "cachedAt": datetime.now(timezone.utc).isoformat(),
        "payload": cache_payload,
    })


def _fetch_json(url: str, debug_logs: list[str]) -> Any:
    debug_logs.append(f"GitHub API URL: {url}")
    with urllib.request.urlopen(_request(url), timeout=FETCH_TIMEOUT_SECONDS) as response:
        debug_logs.append(f"GitHub HTTP status: {getattr(response, 'status', 200)}")
        return json.loads(response.read().decode("utf-8"))


def _classify_error(exc: Exception, debug_logs: list[str]) -> tuple[str, str]:
    if isinstance(exc, urllib.error.HTTPError):
        debug_logs.append(f"GitHub HTTP status: {exc.code}")
        body = ""
        try:
            body = exc.read().decode("utf-8", errors="ignore")
        except Exception:
            body = ""
        if body:
            debug_logs.append(f"GitHub error body: {body[:300]}")
        if exc.code == 404:
            return "github_user_not_found", "未找到 GitHub 用户或公开数据。"
        if exc.code in {403, 429}:
            remaining = exc.headers.get("X-RateLimit-Remaining", "")
            if remaining == "0" or "rate limit" in body.lower():
                return "github_rate_limited", "GitHub API 限流，请稍后再试。"
        return "github_http_error", f"GitHub API 请求失败：HTTP {exc.code}"
    if isinstance(exc, TimeoutError):
        debug_logs.append("GitHub request timeout")
        return "github_timeout", "请求 GitHub 超时。"
    if isinstance(exc, urllib.error.URLError):
        reason = exc.reason
        debug_logs.append(f"GitHub network error: {reason}")
        if isinstance(reason, (TimeoutError, socket.timeout)):
            return "github_timeout", "请求 GitHub 超时。"
        return "github_network_error", "无法访问 GitHub，请检查服务器网络。"
    if isinstance(exc, socket.timeout):
        debug_logs.append("GitHub socket timeout")
        return "github_timeout", "请求 GitHub 超时。"
    debug_logs.append(f"GitHub unknown error: {exc}")
    return "github_unknown_error", f"GitHub 数据读取失败：{exc}"


@router.get("/summary")
def github_summary(username: str = Query("ShrinkShi", min_length=1, max_length=80)):
    safe_username = username.strip().strip("/").split("/")[-1]
    debug_logs = [f"GitHub username: {safe_username}"]
    if not safe_username or not safe_username.replace("-", "").replace("_", "").isalnum():
        return _error_payload("invalid_github_username", "GitHub 用户名格式不正确。", debug_logs)

    try:
        user = _fetch_json(f"https://api.github.com/users/{safe_username}", debug_logs)
    except Exception as exc:
        code, message = _classify_error(exc, debug_logs)
        cached = _cached_payload(safe_username, debug_logs, allow_stale=True)
        if cached:
            return cached
        return _error_payload(code, message, debug_logs)

    try:
        repos = _fetch_json(f"https://api.github.com/users/{safe_username}/repos?per_page=100&sort=updated", debug_logs)
    except Exception as exc:
        code, message = _classify_error(exc, debug_logs)
        debug_logs.append(f"GitHub repos fallback: {code} {message}")
        repos = []

    try:
        events = _fetch_json(f"https://api.github.com/users/{safe_username}/events/public?per_page=100", debug_logs)
    except Exception as exc:
        code, message = _classify_error(exc, debug_logs)
        debug_logs.append(f"GitHub events fallback: {code} {message}")
        events = []

    repo_list = repos if isinstance(repos, list) else []
    event_list = events if isinstance(events, list) else []
    stars = sum(int(repo.get("stargazers_count") or 0) for repo in repo_list if isinstance(repo, dict))
    forks = sum(int(repo.get("forks_count") or 0) for repo in repo_list if isinstance(repo, dict))
    followers = int(user.get("followers") or 0) if isinstance(user, dict) else 0
    public_repos = int(user.get("public_repos") or len(repo_list)) if isinstance(user, dict) else len(repo_list)

    buckets = [0 for _ in range(154)]
    now = datetime.now().timestamp()
    for event in event_list:
        if not isinstance(event, dict):
            continue
        created_at = str(event.get("created_at") or "")
        try:
            timestamp = datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp()
        except ValueError:
            continue
        days_ago = int((now - timestamp) // 86_400)
        if 0 <= days_ago < len(buckets):
            buckets[len(buckets) - 1 - days_ago] += 1

    login = str(user.get("login") or safe_username) if isinstance(user, dict) else safe_username
    payload = {
        "ok": True,
        "username": login,
        "stats": [
            {"icon": "folder", "value": _compact_number(public_repos), "label": "公开仓库"},
            {"icon": "star", "value": _compact_number(stars), "label": "Stars"},
            {"icon": "git-branch", "value": _compact_number(followers), "label": "Followers"},
            {"icon": "fork", "value": _compact_number(forks), "label": "Forks"},
        ],
        "heatmapCells": [min(5, count) for count in buckets],
        "contributionText": f"{login} · {len(event_list)} recent public events",
        "errorCode": "",
        "errorMessage": "",
        "debugLogs": debug_logs,
    }
    _write_cache(safe_username, payload)
    return payload
