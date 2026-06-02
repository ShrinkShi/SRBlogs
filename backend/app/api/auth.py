from datetime import datetime, timedelta, timezone
from uuid import uuid4
from urllib.parse import parse_qs, urlencode, urlparse
import json
import re

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt

from app.config import get_settings
from app.models.schemas import LoginRequest, TokenResponse
from app.services.audit_service import write_audit
from app.services.admin_credentials import verify_admin_password
from app.services.auth_service import create_access_token, require_admin
from app.services.json_service import JsonStore

router = APIRouter(prefix="/auth", tags=["auth"])
VISITOR_COOKIE = "srblogs_visitor_user"
GITHUB_COOKIE = "srblogs_github_user"
GITHUB_STATE_COOKIE = "srblogs_github_state"
GITHUB_RETURN_COOKIE = "srblogs_github_return"
QQ_STATE_COOKIE = "srblogs_qq_state"
QQ_RETURN_COOKIE = "srblogs_qq_return"


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request):
    settings = get_settings()
    if payload.username != settings.admin_username or not verify_admin_password(payload.password, settings):
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


@router.get("/admin/me")
def admin_me(actor: str = Depends(require_admin)):
    return {"username": actor, "role": "admin"}


def _settings_data() -> dict:
    return JsonStore(get_settings().data_path, "settings.json", {}).read()


def _github_oauth_config() -> tuple[str, str]:
    settings = get_settings()
    data = _settings_data()
    gitalk = data.get("gitalkConfig") or (data.get("comments") or {}).get("gitalk") or {}
    client_id = settings.github_oauth_client_id or gitalk.get("clientID", "")
    client_secret = settings.github_oauth_client_secret or gitalk.get("clientSecret", "")
    return str(client_id or ""), str(client_secret or "")


def _qq_oauth_config() -> tuple[str, str]:
    settings = get_settings()
    data = _settings_data()
    comments = data.get("comments") or {}
    qq = data.get("qqOAuth") or comments.get("qq") or {}
    app_id = settings.qq_oauth_app_id or qq.get("appID", "") or qq.get("appId", "") or qq.get("clientID", "")
    app_secret = settings.qq_oauth_app_secret or qq.get("appSecret", "") or qq.get("clientSecret", "")
    return str(app_id or ""), str(app_secret or "")


def _github_configured() -> bool:
    client_id, client_secret = _github_oauth_config()
    return bool(client_id and client_secret)


def _qq_configured() -> bool:
    app_id, app_secret = _qq_oauth_config()
    return bool(app_id and app_secret)


def _frontend_url(request: Request) -> str:
    settings = get_settings()
    fallback = settings.cors_list[0] if settings.cors_list else "http://127.0.0.1:5173"
    raw = str(request.query_params.get("returnTo") or request.query_params.get("return_to") or "").strip()
    if not raw:
        return fallback
    if raw.startswith("/") and not raw.startswith("//"):
        return f"{fallback.rstrip('/')}{raw}"
    parsed = urlparse(raw)
    allowed_origins = {origin.rstrip("/") for origin in settings.cors_list}
    if settings.public_base_url:
        public = urlparse(settings.public_base_url)
        allowed_origins.add(f"{public.scheme}://{public.netloc}".rstrip("/"))
    origin = f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
    if parsed.scheme in {"http", "https"} and origin in allowed_origins:
        return raw
    return fallback


def _encode_visitor_user(user: dict) -> str:
    settings = get_settings()
    payload = {
        "provider": str(user.get("provider") or "github"),
        "sub": str(user.get("id") or user.get("login") or user.get("openid") or ""),
        "name": str(user.get("name") or user.get("nickname") or user.get("login") or ""),
        "avatar": str(user.get("avatar") or user.get("avatar_url") or ""),
        "html_url": str(user.get("html_url") or ""),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def _encode_github_user(user: dict) -> str:
    return _encode_visitor_user({
        "provider": "github",
        "id": user.get("login") or "",
        "name": user.get("name") or user.get("login") or "",
        "avatar": user.get("avatar_url") or user.get("avatar") or "",
        "html_url": user.get("html_url") or "",
        "login": user.get("login") or "",
    })


def read_visitor_user(request: Request) -> dict | None:
    token = request.cookies.get(VISITOR_COOKIE) or request.cookies.get(GITHUB_COOKIE)
    if not token:
        return None
    try:
        payload = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
    except JWTError:
        return None
    provider = payload.get("provider") or "github"
    user_id = payload.get("sub", "")
    if not user_id:
        return None
    return {
        "provider": provider,
        "id": user_id,
        "login": user_id if provider == "github" else "",
        "name": payload.get("name", "") or user_id,
        "avatar": payload.get("avatar", ""),
        "html_url": payload.get("html_url", ""),
    }


def read_github_user(request: Request) -> dict | None:
    user = read_visitor_user(request)
    if not user or user.get("provider") != "github":
        return None
    return {
        "login": user.get("id", ""),
        "name": user.get("name", ""),
        "avatar": user.get("avatar", ""),
        "html_url": user.get("html_url", ""),
    }


def require_visitor_user(request: Request) -> dict:
    user = read_visitor_user(request)
    if not user or not user.get("id"):
        raise HTTPException(status_code=401, detail="请先登录后再留言。")
    return user


def require_github_user(request: Request) -> dict:
    user = read_github_user(request)
    if not user or not user.get("login"):
        raise HTTPException(status_code=401, detail="请先使用 GitHub 登录后再留言。")
    return user


@router.get("/github/me")
def github_me(request: Request):
    return {"configured": _github_configured(), "user": read_github_user(request)}


@router.get("/visitor/me")
def visitor_me(request: Request):
    return {
        "configured": {
            "github": _github_configured(),
            "qq": _qq_configured(),
        },
        "user": read_visitor_user(request),
    }


@router.get("/github/login")
def github_login(request: Request):
    settings = get_settings()
    client_id, _client_secret = _github_oauth_config()
    if not _github_configured():
        raise HTTPException(status_code=503, detail="站点暂未开启 GitHub 留言，请稍后再试或联系站点管理员。")
    state = uuid4().hex
    callback = str(request.url_for("github_callback"))
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
        raise HTTPException(status_code=503, detail="站点暂未开启 GitHub 留言，请稍后再试或联系站点管理员。")
    if not state or not expected_state or state != expected_state:
        raise HTTPException(status_code=400, detail="Invalid GitHub OAuth state")
    callback = str(request.url_for("github_callback"))
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
    encoded = _encode_github_user(user)
    response.set_cookie(VISITOR_COOKIE, encoded, httponly=True, samesite="lax", secure=secure, max_age=7 * 86400)
    response.set_cookie(GITHUB_COOKIE, encoded, httponly=True, samesite="lax", secure=secure, max_age=7 * 86400)
    response.delete_cookie(GITHUB_STATE_COOKIE)
    response.delete_cookie(GITHUB_RETURN_COOKIE)
    return response


@router.post("/github/logout")
def github_logout(response: Response):
    response.delete_cookie(GITHUB_COOKIE)
    response.delete_cookie(VISITOR_COOKIE)
    return {"ok": True}


@router.post("/visitor/logout")
def visitor_logout(response: Response):
    response.delete_cookie(VISITOR_COOKIE)
    response.delete_cookie(GITHUB_COOKIE)
    return {"ok": True}


@router.get("/qq/login")
def qq_login(request: Request):
    settings = get_settings()
    app_id, _app_secret = _qq_oauth_config()
    if not _qq_configured():
        raise HTTPException(status_code=503, detail="站点暂未开启 QQ 留言，请稍后再试或联系站点管理员。")
    state = uuid4().hex
    callback = str(request.url_for("qq_callback"))
    params = urlencode({
        "response_type": "code",
        "client_id": app_id,
        "redirect_uri": callback,
        "state": state,
        "scope": "get_user_info",
    })
    response = RedirectResponse(f"https://graph.qq.com/oauth2.0/authorize?{params}")
    secure = settings.app_env == "production"
    response.set_cookie(QQ_STATE_COOKIE, state, httponly=True, samesite="lax", secure=secure, max_age=600)
    response.set_cookie(QQ_RETURN_COOKIE, _frontend_url(request), httponly=True, samesite="lax", secure=secure, max_age=600)
    return response


@router.get("/qq/callback")
async def qq_callback(request: Request, code: str = "", state: str = ""):
    settings = get_settings()
    app_id, app_secret = _qq_oauth_config()
    expected_state = request.cookies.get(QQ_STATE_COOKIE)
    return_to = request.cookies.get(QQ_RETURN_COOKIE) or (settings.cors_list[0] if settings.cors_list else "http://127.0.0.1:5173")
    if not _qq_configured():
        raise HTTPException(status_code=503, detail="站点暂未开启 QQ 留言，请稍后再试或联系站点管理员。")
    if not state or not expected_state or state != expected_state:
        raise HTTPException(status_code=400, detail="Invalid QQ OAuth state")
    callback = str(request.url_for("qq_callback"))
    async with httpx.AsyncClient(timeout=15) as client:
        token_resp = await client.get(
            "https://graph.qq.com/oauth2.0/token",
            params={
                "grant_type": "authorization_code",
                "client_id": app_id,
                "client_secret": app_secret,
                "code": code,
                "redirect_uri": callback,
            },
        )
        token_data = parse_qs(token_resp.text)
        access_token = (token_data.get("access_token") or [""])[0]
        if not access_token:
            raise HTTPException(status_code=400, detail="QQ OAuth token exchange failed")
        me_resp = await client.get("https://graph.qq.com/oauth2.0/me", params={"access_token": access_token})
        matched = re.search(r"\{.*\}", me_resp.text)
        if not matched:
            raise HTTPException(status_code=400, detail="QQ OAuth openid lookup failed")
        openid_data = json.loads(matched.group(0))
        openid = str(openid_data.get("openid") or "")
        if not openid:
            raise HTTPException(status_code=400, detail="QQ OAuth openid lookup failed")
        profile_resp = await client.get(
            "https://graph.qq.com/user/get_user_info",
            params={"access_token": access_token, "oauth_consumer_key": app_id, "openid": openid},
        )
        profile = profile_resp.json()
    user = {
        "provider": "qq",
        "id": openid,
        "name": profile.get("nickname") or "QQ User",
        "avatar": profile.get("figureurl_qq_2") or profile.get("figureurl_qq_1") or profile.get("figureurl_2") or "",
    }
    response = RedirectResponse(return_to)
    secure = settings.app_env == "production"
    response.set_cookie(VISITOR_COOKIE, _encode_visitor_user(user), httponly=True, samesite="lax", secure=secure, max_age=7 * 86400)
    response.delete_cookie(QQ_STATE_COOKIE)
    response.delete_cookie(QQ_RETURN_COOKIE)
    return response
