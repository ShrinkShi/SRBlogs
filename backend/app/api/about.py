from __future__ import annotations

import re
import smtplib
import time
from copy import deepcopy
from datetime import datetime
from email.message import EmailMessage
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from app.config import get_settings
from app.models.schemas import JsonWrite
from app.services.audit_service import write_audit
from app.services.auth_service import require_admin
from app.services.file_store import resolve_data_path, safe_read_text, safe_write_text
from app.services.json_service import JsonStore

router = APIRouter(prefix="/about", tags=["about"])
about_page_router = APIRouter(tags=["about-page"])
contact_router = APIRouter(prefix="/contact", tags=["contact"])


DEFAULT_ABOUT_PAGE: dict[str, Any] = {
    "hero": {
        "status": "Available for opportunities",
        "eyebrow": "你好，我是",
        "name": "Shrink",
        "role": "全栈开发工程师",
        "description": "物联网工程专业学生，热衷于 MOD、游戏引擎，热爱软件、Web 应用开发。\n致力于用技术创造价值",
        "primaryButtonText": "查看作品",
        "primaryButtonUrl": "/projects",
        "secondaryButtonText": "联系我",
        "stats": [
            {"value": "4", "suffix": "+", "label": "年经验"},
            {"value": "20", "suffix": "+", "label": "个项目"},
            {"value": "1,000", "suffix": "+", "label": "次提交"},
        ],
    },
    "about": {
        "badge": "<about />",
        "title": "关于我",
        "paragraphs": [
            "我是一名充满热情的全栈开发工程师，拥有丰富的 Web 应用开发经验。",
            "在多年的开发生涯中，我参与并主导了多个企业级项目的架构设计与开发工作。从前端的交互体验到后端的系统架构，从数据库设计到云端部署，我始终追求代码的优雅性和系统的可靠性。",
            "我相信技术的力量，热爱开源社区，持续学习新技术并将其应用到实际项目中。在工作之余，我也喜欢通过技术博客和开源项目与社区分享知识。",
        ],
        "highlightWords": ["全栈开发工程师"],
        "skills": [
            {"icon": "rocket", "title": "全栈开发", "description": "前端与后端的完整技术栈"},
            {"icon": "cloud", "title": "云原生架构", "description": "Docker、K8s、微服务架构"},
            {"icon": "bot", "title": "AI 应用", "description": "LLM 集成与智能应用开发"},
        ],
        "codeProfile": {
            "variableName": "Shrink",
            "name": "Shrink",
            "role": "Freelance Developer",
            "location": "BeiJing, China CN",
            "languages": ["python", "Java", "c#", "c++", "Vue/Nuxt"],
            "github": "github.com/ShrinkShi",
        },
    },
    "github": {
        "badge": "<github />",
        "titlePrefix": "GitHub",
        "titleAccent": "活动",
        "stats": [
            {"icon": "folder", "value": "20", "label": "公开仓库"},
            {"icon": "star", "value": "2616", "label": "Stars"},
            {"icon": "git-branch", "value": "79", "label": "Followers"},
            {"icon": "fork", "value": "837", "label": "Forks"},
        ],
        "contributionText": "07836246 · 2,108 contributions",
    },
    "contact": {
        "badge": "<contact />",
        "title": "联系我",
        "headline": "让我们一起创造价值",
        "description": "无论是工作机会、项目合作还是技术交流，都欢迎与我联系，期待与您的交流！",
        "email": "1363072460@qq.com",
        "github": "github.com/ShrinkShi",
        "githubUrl": "https://github.com/ShrinkShi",
        "website": "www.shrink.asia",
        "websiteUrl": "https://www.shrink.asia",
        "qq": "1363072460",
        "wechat": "请填写微信号",
        "mailTo": "1363072460@qq.com",
    },
}

_CONTACT_BUCKET: dict[str, list[float]] = {}
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ContactPayload(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=160)
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("name", "email", "message")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("email")
    @classmethod
    def email_format(cls, value: str) -> str:
        if not _EMAIL_RE.match(value):
            raise ValueError("邮箱格式不正确")
        return value


def _about_store() -> JsonStore:
    return JsonStore(get_settings().data_path, "about_page.json", DEFAULT_ABOUT_PAGE)


def _deep_merge(default: Any, saved: Any) -> Any:
    if isinstance(default, dict):
        result = deepcopy(default)
        if isinstance(saved, dict):
            for key, value in saved.items():
                result[key] = _deep_merge(default.get(key), value) if key in default else value
        return result
    if isinstance(default, list):
        return saved if isinstance(saved, list) else deepcopy(default)
    return deepcopy(default) if saved is None else saved


def _read_about_page() -> dict[str, Any]:
    data = _about_store().read()
    return _deep_merge(DEFAULT_ABOUT_PAGE, data if isinstance(data, dict) else {})


def _validate_urlish(value: str, field: str) -> None:
    text = (value or "").strip()
    if text and not (text.startswith("/") or text.startswith("http://") or text.startswith("https://")):
        raise HTTPException(status_code=400, detail=f"{field} 必须是站内路径或 http(s) 链接。")


def _validate_about_page(data: dict[str, Any]) -> None:
    hero = data.get("hero") if isinstance(data.get("hero"), dict) else {}
    if not str(hero.get("name", "")).strip():
        raise HTTPException(status_code=400, detail="Hero 名称不能为空。")
    _validate_urlish(str(hero.get("primaryButtonUrl", "")), "查看作品按钮链接")

    contact = data.get("contact") if isinstance(data.get("contact"), dict) else {}
    if contact.get("email") and not _EMAIL_RE.match(str(contact["email"])):
        raise HTTPException(status_code=400, detail="联系邮箱格式不正确。")
    for key in ("githubUrl", "websiteUrl"):
        _validate_urlish(str(contact.get(key, "")), key)


@about_page_router.get("/about-page")
def read_about_page():
    return _read_about_page()


@about_page_router.get("/admin/about-page", dependencies=[Depends(require_admin)])
def read_admin_about_page():
    return _read_about_page()


@about_page_router.put("/admin/about-page")
def write_admin_about_page(payload: JsonWrite, actor: str = Depends(require_admin)):
    incoming = payload.data if isinstance(payload.data, dict) else {}
    data = _deep_merge(DEFAULT_ABOUT_PAGE, incoming)
    _validate_about_page(data)
    _about_store().write(data)
    write_audit(
        actor=actor,
        action="about_page.update",
        resource="about",
        target="about_page.json",
        result="success",
        message="新版关于页结构化配置已更新",
    )
    return data


def _check_contact_rate(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    recent = [stamp for stamp in _CONTACT_BUCKET.get(ip, []) if now - stamp < 60]
    if len(recent) >= 3:
        raise HTTPException(status_code=429, detail="提交过于频繁，请稍后再试。")
    recent.append(now)
    _CONTACT_BUCKET[ip] = recent


@contact_router.post("/send")
def send_contact(payload: ContactPayload, request: Request):
    settings = get_settings()
    if not settings.contact_mail_enabled:
        raise HTTPException(status_code=503, detail="联系表单暂未启用")
    if not settings.smtp_host or not settings.smtp_username or not settings.smtp_password:
        raise HTTPException(status_code=503, detail="联系表单暂未启用")

    _check_contact_rate(request)
    about_page = _read_about_page()
    mail_to = settings.contact_mail_to or about_page.get("contact", {}).get("mailTo") or "1363072460@qq.com"

    msg = EmailMessage()
    msg["Subject"] = f"SRBlogs 联系表单 - {payload.name}"
    msg["From"] = settings.smtp_from or settings.smtp_username
    msg["To"] = mail_to
    msg.set_content(
        "\n".join(
            [
                f"姓名：{payload.name}",
                f"邮箱：{payload.email}",
                "来源页面：/about",
                f"提交时间：{datetime.now().isoformat(timespec='seconds')}",
                "",
                "留言：",
                payload.message,
            ]
        )
    )

    try:
        if settings.smtp_use_ssl:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=12) as smtp:
                smtp.login(settings.smtp_username, settings.smtp_password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=12) as smtp:
                smtp.starttls()
                smtp.login(settings.smtp_username, settings.smtp_password)
                smtp.send_message(msg)
    except Exception:
        raise HTTPException(status_code=503, detail="邮件发送失败，请稍后再试。")

    write_audit(
        actor="visitor",
        action="contact.send",
        resource="contact",
        target=mail_to,
        result="success",
        message="联系表单邮件已发送",
        ip=request.client.host if request.client else "",
        detail={"name": payload.name, "email": payload.email},
    )
    return {"ok": True, "message": "消息已发送"}


@router.get("")
def get_about():
    file = resolve_data_path("about.md")
    if not file.exists():
        safe_write_text(file, "# About\n\nWrite your introduction here.\n", make_backup=False)
    return {"content": safe_read_text(file)}


@router.put("")
def update_about(payload: JsonWrite, actor: str = Depends(require_admin)):
    file = resolve_data_path("about.md")
    content = str(payload.data.get("content", "")) if isinstance(payload.data, dict) else str(payload.data)
    safe_write_text(file, content)
    write_audit(
        actor=actor,
        action="about.update",
        resource="about",
        target="about.md",
        result="success",
        message="兼容 About Markdown 已更新",
    )
    return {"ok": True}
