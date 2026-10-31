"""API request/response schemas."""

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """User chat request."""

    message: str = Field(
        min_length=1,
        max_length=500,
        description="Текст запроса пользователя",
    )

    @field_validator("message")
    @classmethod
    def message_not_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Сообщение не может состоять только из пробелов")
        return v


class ChatResponse(BaseModel):
    """API response."""

    message: dict
    status: str = "ok"
