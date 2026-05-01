from typing import Any, Optional
from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class ContentMeta(BaseModel):
    title: str = "未命名"
    date: str = ""
    tags: list[str] = Field(default_factory=list)
    draft: bool = False
    cover: str = ""
    summary: str = ""


class ContentItem(BaseModel):
    slug: str
    meta: ContentMeta
    content: str = ""


class ContentWrite(BaseModel):
    slug: str
    meta: ContentMeta
    content: str


class JsonWrite(BaseModel):
    data: Any


class CommentCreate(BaseModel):
    author: str = Field(min_length=1, max_length=40)
    email: Optional[str] = Field(default="", max_length=120)
    content: str = Field(min_length=1, max_length=1000)


class CommentItem(BaseModel):
    id: str
    author: str
    email: str = ""
    content: str
    created_at: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    provider: str = "a"
    messages: list[ChatMessage]
    stream: bool = False
