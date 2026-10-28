"""Schemas and request/response models."""

from pydantic import BaseModel, field_validator


class ChatRequest(BaseModel):
    countryId: int
    message: str

    @field_validator("countryId")
    @classmethod
    def country_id_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("countryId must be a positive integer")
        return v

    @field_validator("message")
    @classmethod
    def message_not_empty_and_not_too_long(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("message must not be empty")
        if len(v) > 1000:
            raise ValueError("message must not exceed 1000 characters")
        return v


class ChatResponse(BaseModel):
    countryId: int
    message: str
    status: str
