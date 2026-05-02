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
    draft: bool = False
    cover: str = ""
    summary: str = ""

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

    @field_validator("author", "content")
    @classmethod
    def no_blank_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("field cannot be blank")
        return value.strip()


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
