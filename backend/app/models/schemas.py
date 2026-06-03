import re
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class ContentMeta(BaseModel):
    title: str = "Untitled"
    date: str = ""
    tags: list[str] = Field(default_factory=list)
    tagColors: dict[str, str] = Field(default_factory=dict)
    draft: bool = False
    cover: str = ""
    summary: str = ""
    images: list[str] = Field(default_factory=list)
    location: str = ""
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0

    @field_validator("title")
    @classmethod
    def title_required(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("title is required")
        return value.strip()


class ContentItem(BaseModel):
    slug: str
    meta: ContentMeta
    content: str = ""
    updatedAt: str = ""


class ContentWrite(BaseModel):
    slug: str
    meta: ContentMeta
    content: str


class JsonWrite(BaseModel):
    data: Any


class CommentAttachment(BaseModel):
    url: str
    filename: str = ""
    originalName: str = ""
    size: int = 0
    kind: str = "file"


class CommentCreate(BaseModel):
    author: str = Field(default="", max_length=40)
    email: Optional[str] = Field(default="", max_length=120)
    content: str = Field(min_length=1, max_length=5000)
    parentId: str = Field(default="", max_length=80)
    attachments: list[CommentAttachment] = Field(default_factory=list, max_length=5)

    @field_validator("content")
    @classmethod
    def no_blank_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("field cannot be blank")
        return value.strip()

    @field_validator("author")
    @classmethod
    def clean_author(cls, value: str) -> str:
        return (value or "").strip()

    @field_validator("email")
    @classmethod
    def email_format_optional(cls, value: Optional[str]) -> str:
        text = (value or "").strip()
        if text and not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", text):
            raise ValueError("email format is invalid")
        return text


class CommentItem(BaseModel):
    id: str
    author: str
    email: str = ""
    content: str
    created_at: str
    avatar: str = ""
    githubLogin: str = ""
    provider: str = ""
    providerId: str = ""
    parentId: str = ""
    replyTo: dict[str, str] = Field(default_factory=dict)
    attachments: list[CommentAttachment] = Field(default_factory=list)


class CommentIndexItem(BaseModel):
    resource: str
    slug: str
    count: int
    updatedAt: str = ""
    title: str = ""


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    provider: str = "a"
    messages: list[ChatMessage]
    stream: bool = False
