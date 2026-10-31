"""Unit tests for API."""

import pytest

from api.schemas import ChatRequest


class TestChatEndpoint:
    """Tests for the chat endpoint."""

    def test_valid_request(self):
        """Valid request is accepted."""
        data = {"message": "Отели в Турции"}
        result = ChatRequest.model_validate(data)
        assert result.message == "Отели в Турции"

    def test_message_empty(self):
        """Empty message is rejected."""
        with pytest.raises(Exception):
            ChatRequest.model_validate({"message": ""})

    def test_message_empty_string(self):
        """Empty string message is rejected."""
        with pytest.raises(Exception):
            ChatRequest.model_validate({"message": ""})

    def test_message_too_long(self):
        """Overly long message is rejected."""
        with pytest.raises(Exception):
            ChatRequest.model_validate({"message": "a" * 501})

    def test_message_whitespace(self):
        """Whitespace-only message is rejected."""
        with pytest.raises(Exception):
            ChatRequest.model_validate({"message": "   "})
