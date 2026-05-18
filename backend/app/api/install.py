from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.services.install_service import (
    InstallError,
    InstallRateLimitError,
    check_rate_limit,
    clear_failed_attempts,
    install,
    install_status,
    is_installed,
    register_failed_attempt,
)

router = APIRouter(prefix="/install", tags=["install"])


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


@router.get("/status")
def status():
    return install_status()


@router.post("")
async def run_install(request: Request):
    if is_installed():
        raise HTTPException(status_code=403, detail="SRBlogs 已完成安装。")
    ip = _client_ip(request)
    try:
        check_rate_limit(ip)
    except InstallRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    try:
        payload: Any = await request.json()
        if not isinstance(payload, dict):
            raise InstallError("安装参数格式不正确。")
        result = install(payload)
        clear_failed_attempts(ip)
        return result
    except HTTPException:
        raise
    except InstallRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except InstallError as exc:
        register_failed_attempt(ip)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PermissionError as exc:
        register_failed_attempt(ip)
        raise HTTPException(status_code=500, detail="无法写入安装配置，请检查 /etc/srblogs/backend.env 权限。") from exc
