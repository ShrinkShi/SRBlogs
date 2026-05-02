from fastapi import APIRouter, HTTPException, Request

from app.config import get_settings
from app.models.schemas import LoginRequest, TokenResponse
from app.services.audit_service import write_audit
from app.services.auth_service import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


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
