from fastapi import APIRouter, HTTPException
from app.config import get_settings
from app.models.schemas import LoginRequest, TokenResponse
from app.services.auth_service import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    settings = get_settings()
    if payload.username != settings.admin_username or payload.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return TokenResponse(access_token=create_access_token(payload.username))
