"""Unit tests for LLM module."""

import pytest

from llm.prompts import (
    build_analyst_prompt,
    build_travel_expert_prompt,
)
from llm.model import chat_completion
from llm.schemas import AnalystResponse


class TestBuildAnalystPrompt:
    """Tests for analyst prompt builder."""

    def test_returns_string(self):
        """Returns a string (system prompt only)."""
        result = build_analyst_prompt("test message")
        assert isinstance(result, str)

    def test_contains_user_message(self):
        """Prompt includes user message."""
        result = build_analyst_prompt("Какие отели в Турции?")
        assert "Какие отели в Турции?" in result

    def test_contains_json_instruction(self):
        """Prompt instructs to return JSON."""
        result = build_analyst_prompt("test")
        assert "JSON" in result

    def test_contains_country_instruction(self):
        """Prompt instructs to extract country."""
        result = build_analyst_prompt("test")
        assert "country" in result


class TestBuildTravelExpertPrompt:
    """Tests for travel expert prompt builder."""

    def test_returns_string(self):
        """Returns a string (system prompt only)."""
        result = build_travel_expert_prompt("Турция", '{"country": "Турция", "region": ["Анталья"]}')
        assert isinstance(result, str)

    def test_system_prompt_instructs_json(self):
        """System prompt instructs to return JSON."""
        result = build_travel_expert_prompt("Турция", '{"country": "Турция"}')
        assert "JSON" in result

    def test_includes_country_name(self):
        """System prompt includes the country name."""
        result = build_travel_expert_prompt("Турция", '{"country": "Турция"}')
        assert "Турция" in result

    def test_includes_json_data(self):
        """System prompt includes the json_data."""
        result = build_travel_expert_prompt("Турция", '{"country": "Турция", "region": ["Анталья"]}')
        assert "Анталья" in result

    def test_includes_hotel_fields(self):
        """System prompt includes all hotel fields."""
        result = build_travel_expert_prompt("Турция", '{"country": "Турция"}')
        assert "hotel" in result
        assert "Описание" in result or "description" in result
        assert "звёзд" in result or "category" in result
        assert "Преимущества" in result or "advantages" in result
        assert "Нюансы" in result or "nuance" in result
        assert "kindOfLeisure" in result

    def test_includes_travel_recommendation(self):
        """System prompt includes travelRecommendation."""
        result = build_travel_expert_prompt("Турция", '{"country": "Турция"}')
        assert "travelRecommendation" in result


class TestChatCompletion:
    """Tests for chat_completion function."""

    def test_no_override_raises_error(self):
        """Without system_prompt_override, raises RuntimeError."""
        with pytest.raises(RuntimeError, match="Сервис временно недоступен"):
            chat_completion("dummy_key", 0, "test")
