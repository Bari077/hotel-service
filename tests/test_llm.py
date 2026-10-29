"""Unit tests for LLM module."""

import pytest

from llm.prompts import (
    build_analyst_prompt,
    build_travel_expert_prompt,
    build_travel_expert_user_prompt,
)
from llm.model import chat_completion


class TestBuildAnalystPrompt:
    """Tests for analyst prompt builder."""

    def test_returns_string(self):
        """Returns a string (system prompt only)."""
        result = build_analyst_prompt("Турция", "test message")
        assert isinstance(result, str)

    def test_contains_country(self):
        """Prompt includes the country name."""
        result = build_analyst_prompt("Египет", "test")
        assert "Египет" in result

    def test_contains_json_schema(self):
        """Prompt includes JSON schema."""
        result = build_analyst_prompt("Турция", "test")
        assert '"country"' in result
        assert '"region"' in result
        assert '"category"' in result
        assert '"preferences"' in result

    def test_contains_user_message(self):
        """Prompt includes user message."""
        result = build_analyst_prompt("Тайланд", "Какие отели?")
        assert "Тайланд" in result
        assert "Какие отели?" in result


class TestBuildTravelExpertPrompt:
    """Tests for travel expert prompt builder."""

    def test_returns_string(self):
        """Returns a string (system prompt only)."""
        result = build_travel_expert_prompt('{"country": "Турция"}')
        assert isinstance(result, str)

    def test_system_prompt_instructs_json(self):
        """System prompt instructs to return JSON."""
        result = build_travel_expert_prompt('{"country": "Турция"}')
        assert "JSON" in result

    def test_includes_json_data(self):
        """System prompt includes the json_data."""
        result = build_travel_expert_prompt('{"country": "Турция", "region": ["Анталья"]}')
        assert "Турция" in result
        assert "Анталья" in result

    def test_includes_hotel_fields(self):
        """System prompt includes all hotel fields."""
        result = build_travel_expert_prompt('{"country": "Турция"}')
        assert "hotel" in result
        assert "description" in result
        assert "category" in result
        assert "advantages" in result
        assert "nuance" in result
        assert "kindOfLeasure" in result

    def test_includes_travel_recommendation(self):
        """System prompt includes travelRecommendation."""
        result = build_travel_expert_prompt('{"country": "Турция"}')
        assert "travelRecommendation" in result

    def test_includes_user_prompt_text(self):
        """System prompt includes the natural-language user prompt."""
        result = build_travel_expert_prompt(
            '{"country": "Турция", "region": ["Анталья"], "category": ["5"], "preferences": ["у моря"]}'
        )
        assert "Какие отели" in result
        assert "5 звезд" in result
        assert "у моря" in result
        assert "в регионе Анталья" in result


class TestBuildTravelExpertUserPrompt:
    """Tests for travel expert user prompt builder."""

    def test_single_region(self):
        """Single region in region_phrase."""
        user_prompt = build_travel_expert_user_prompt(
            '{"country": "Турция", "region": ["Анталья"], "category": [], "preferences": []}'
        )
        assert "в регионе Анталья" in user_prompt

    def test_multiple_regions(self):
        """Multiple regions in region_phrase."""
        user_prompt = build_travel_expert_user_prompt(
            '{"country": "Турция", "region": ["Анталья", "Бодрум"], "category": [], "preferences": []}'
        )
        assert "в регионах Анталья, Бодрум" in user_prompt

    def test_region_string(self):
        """Region as string."""
        user_prompt = build_travel_expert_user_prompt(
            '{"country": "Турция", "region": "Анталья", "category": [], "preferences": []}'
        )
        assert "в регионе Анталья" in user_prompt

    def test_no_region(self):
        """No region specified."""
        user_prompt = build_travel_expert_user_prompt(
            '{"country": "Турция", "region": [], "category": [], "preferences": []}'
        )
        assert "в регионе" not in user_prompt

    def test_category(self):
        """Category (stars) in user_prompt."""
        user_prompt = build_travel_expert_user_prompt(
            '{"country": "Турция", "region": [], "category": ["5"], "preferences": []}'
        )
        assert "5 звезд" in user_prompt

    def test_preferences(self):
        """Preferences in user_prompt."""
        user_prompt = build_travel_expert_user_prompt(
            '{"country": "Турция", "region": [], "category": [], "preferences": ["у моря", "все включено"]}'
        )
        assert "у моря" in user_prompt
        assert "все включено" in user_prompt

    def test_clean_whitespace(self):
        """Result has clean single whitespace."""
        user_prompt = build_travel_expert_user_prompt(
            '{"country": "Турция", "region": [], "category": [], "preferences": []}'
        )
        assert "  " not in user_prompt

    def test_null_category(self):
        """Null category should not produce 'None звезд'."""
        user_prompt = build_travel_expert_user_prompt(
            '{"country": "Турция", "region": [], "category": null, "preferences": []}'
        )
        assert "None" not in user_prompt
        assert "звезд" not in user_prompt

    def test_null_preferences(self):
        """Null preferences should not produce 'Мои предпочтения: None'."""
        user_prompt = build_travel_expert_user_prompt(
            '{"country": "Турция", "region": [], "category": [], "preferences": null}'
        )
        assert "Мои предпочтения: None" not in user_prompt
        assert "None" not in user_prompt

    def test_null_region(self):
        """Null region should not produce 'в регионе None'."""
        user_prompt = build_travel_expert_user_prompt(
            '{"country": "Турция", "region": null, "category": [], "preferences": []}'
        )
        assert "в регионе" not in user_prompt


class TestChatCompletion:
    """Tests for chat_completion function."""

    def test_no_override_raises_error(self):
        """Without system_prompt_override, raises RuntimeError."""
        with pytest.raises(RuntimeError, match="Сервис временно недоступен"):
            chat_completion("dummy_key", 1, "test")
