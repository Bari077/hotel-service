"""API request/response schemas."""

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """User chat request."""

    message: str = Field(
        description="Текст запроса пользователя",
    )

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("Сообщение не может быть пустым")
        return v

    @field_validator("message")
    @classmethod
    def message_not_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Сообщение не может состоять только из пробелов")
        return v

    @field_validator("message")
    @classmethod
    def message_not_too_long(cls, v: str) -> str:
        if len(v) > 500:
            raise ValueError("Сообщение слишком длинное (максимум 500 символов)")
        return v
