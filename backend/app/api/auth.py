from datetime import datetime, timedelta, timezone
from uuid import uuid4

import httpx
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt

from app.config import get_settings
from app.models.schemas import LoginRequest, TokenResponse
from app.services.audit_service import write_audit
from app.services.auth_service import create_access_token
from app.services.json_service import JsonStore

router = APIRouter(prefix="/auth", tags=["auth"])
GITHUB_COOKIE = "srblogs_github_user"
GITHUB_STATE_COOKIE = "srblogs_github_state"
GITHUB_RETURN_COOKIE = "srblogs_github_return"


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request):
    settings = get_settings()
    if payload.username != settings.admin_username or payload.password != settings.admin_password:
        write_audit(
            actor=payload.username or "unknown",
            action="auth.login",
            resource="auth",
            target=payload.username,
            result="failed",
            message="Login failed",
            ip=request.client.host if request.client else "",
        )
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    write_audit(
        actor=payload.username,
        action="auth.login",
        resource="auth",
        target=payload.username,
        result="success",
        message="Login success",
        ip=request.client.host if request.client else "",
    )
    return TokenResponse(access_token=create_access_token(payload.username))


def _settings_data() -> dict:
    return JsonStore(get_settings().data_path, "settings.json", {}).read()


def _github_oauth_config() -> tuple[str, str]:
    settings = get_settings()
    data = _settings_data()
    gitalk = data.get("gitalkConfig") or (data.get("comments") or {}).get("gitalk") or {}
    client_id = settings.github_oauth_client_id or gitalk.get("clientID", "")
    client_secret = settings.github_oauth_client_secret or gitalk.get("clientSecret", "")
    return str(client_id or ""), str(client_secret or "")


def _github_configured() -> bool:
    client_id, client_secret = _github_oauth_config()
    return bool(client_id and client_secret)


def _frontend_url(request: Request) -> str:
    settings = get_settings()
    fallback = settings.cors_list[0] if settings.cors_list else "http://127.0.0.1:5173"
    return str(request.query_params.get("return_to") or fallback)


def _encode_github_user(user: dict) -> str:
    settings = get_settings()
    payload = {
        "sub": str(user.get("login") or ""),
        "name": str(user.get("name") or user.get("login") or ""),
        "avatar": str(user.get("avatar_url") or ""),
        "html_url": str(user.get("html_url") or ""),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def read_github_user(request: Request) -> dict | None:
    token = request.cookies.get(GITHUB_COOKIE)
    if not token:
        return None
    try:
        payload = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
    except JWTError:
        return None
    return {
        "login": payload.get("sub", ""),
        "name": payload.get("name", ""),
        "avatar": payload.get("avatar", ""),
        "html_url": payload.get("html_url", ""),
    }


def require_github_user(request: Request) -> dict:
    user = read_github_user(request)
    if not user or not user.get("login"):
        raise HTTPException(status_code=401, detail="GitHub login is required to comment")
    return user


@router.get("/github/me")
def github_me(request: Request):
    return {"configured": _github_configured(), "user": read_github_user(request)}


@router.get("/github/login")
def github_login(request: Request):
    settings = get_settings()
    client_id, _client_secret = _github_oauth_config()
    if not _github_configured():
        raise HTTPException(status_code=503, detail="GitHub OAuth is not configured")
    state = uuid4().hex
    callback = f"{settings.public_base_url.rstrip('/')}/api/auth/github/callback"
    url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={callback}"
        f"&state={state}"
        "&scope=read:user"
    )
    response = RedirectResponse(url)
    secure = settings.app_env == "production"
    response.set_cookie(GITHUB_STATE_COOKIE, state, httponly=True, samesite="lax", secure=secure, max_age=600)
    response.set_cookie(GITHUB_RETURN_COOKIE, _frontend_url(request), httponly=True, samesite="lax", secure=secure, max_age=600)
    return response


@router.get("/github/callback")
async def github_callback(request: Request, code: str = "", state: str = ""):
    settings = get_settings()
    client_id, client_secret = _github_oauth_config()
    expected_state = request.cookies.get(GITHUB_STATE_COOKIE)
    return_to = request.cookies.get(GITHUB_RETURN_COOKIE) or (settings.cors_list[0] if settings.cors_list else "http://127.0.0.1:5173")
    if not _github_configured():
        raise HTTPException(status_code=503, detail="GitHub OAuth is not configured")
    if not state or not expected_state or state != expected_state:
        raise HTTPException(status_code=400, detail="Invalid GitHub OAuth state")
    callback = f"{settings.public_base_url.rstrip('/')}/api/auth/github/callback"
    async with httpx.AsyncClient(timeout=15) as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": callback,
                "state": state,
            },
            headers={"Accept": "application/json"},
        )
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="GitHub OAuth token exchange failed")
        user_resp = await client.get("https://api.github.com/user", headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"})
        user_resp.raise_for_status()
        user = user_resp.json()
    response = RedirectResponse(return_to)
    secure = settings.app_env == "production"
    response.set_cookie(GITHUB_COOKIE, _encode_github_user(user), httponly=True, samesite="lax", secure=secure, max_age=7 * 86400)
    response.delete_cookie(GITHUB_STATE_COOKIE)
    response.delete_cookie(GITHUB_RETURN_COOKIE)
    return response


@router.post("/github/logout")
def github_logout(response: Response):
    response.delete_cookie(GITHUB_COOKIE)
    return {"ok": True}
