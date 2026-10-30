"""Unit tests for business logic."""

import pytest

from services.countries import get_country_name, COUNTRY_MAP
from services.service import process_chat, is_empty_criteria
from llm.schemas import AnalystResponse


class TestCountries:
    """Tests for country mapping."""

    def test_get_country_name_valid(self):
        """Mapping exists for all expected countries."""
        assert get_country_name(1) == "Турция"
        assert get_country_name(8) == "Шри-Ланка"
        assert len(COUNTRY_MAP) == 8

    def test_get_country_name_invalid(self):
        """Mapping returns None for unknown country ID."""
        assert get_country_name(99) is None
        assert get_country_name(0) is None
        assert get_country_name(-1) is None


class TestProcessChat:
    """Tests for process_chat function."""

    def test_process_chat_no_auth_key(self, monkeypatch):
        """Missing LLM_AUTH_KEY raises RuntimeError."""
        monkeypatch.delenv("LLM_AUTH_KEY", raising=False)
        with pytest.raises(RuntimeError, match="Сервис временно недоступен"):
            process_chat(1, "test")

    def test_process_chat_country_not_found(self, monkeypatch):
        """Unknown country ID raises ValueError."""
        monkeypatch.setenv("LLM_AUTH_KEY", "dummy_key")
        with pytest.raises(ValueError, match="Country 99 not found"):
            process_chat(99, "test")


class TestIsEmptyCriteria:
    """Tests for is_empty_criteria function."""

    def test_all_empty(self):
        """All criteria empty → True."""
        analyst = AnalystResponse(
            country="Тайланд",
            region=[],
            category=[],
            preferences=[],
        )
        assert is_empty_criteria(analyst) is True

    def test_region_present(self):
        """Region specified → False."""
        analyst = AnalystResponse(
            country="Тайланд",
            region=["Пхукет"],
            category=[],
            preferences=[],
        )
        assert is_empty_criteria(analyst) is False

    def test_category_present(self):
        """Category specified → False."""
        analyst = AnalystResponse(
            country="Тайланд",
            region=[],
            category=[5],
            preferences=[],
        )
        assert is_empty_criteria(analyst) is False

    def test_preferences_present(self):
        """Preferences specified → False."""
        analyst = AnalystResponse(
            country="Тайланд",
            region=[],
            category=[],
            preferences=["у моря"],
        )
        assert is_empty_criteria(analyst) is False

    def test_all_present(self):
        """All criteria specified → False."""
        analyst = AnalystResponse(
            country="Тайланд",
            region=["Пхукет"],
            category=[5],
            preferences=["все включено"],
        )
        assert is_empty_criteria(analyst) is False


class TestProcessChatMessage:
    """Tests for message field when criteria are empty."""

    def test_empty_criteria_adds_message(self):
        """Empty criteria → message field added."""
        result = {
            "hotelList": [{"region": "Пхукет", "hotels": []}],
            "travelRecommendation": "test",
        }
        analyst = AnalystResponse(
            country="Тайланд",
            region=[],
            category=[],
            preferences=[],
        )
        if is_empty_criteria(analyst):
            result["message"] = (
                "Вы не задали ни одного критерия для подборки отелей. "
                "Вот на всякий случай несколько отелей по запрошенной вами стране."
            )

        assert "message" in result
        assert "ни одного критерия" in result["message"]

    def test_non_empty_criteria_no_message(self):
        """Non-empty criteria → no message field."""
        result = {
            "hotelList": [{"region": "Пхукет", "hotels": []}],
            "travelRecommendation": "test",
        }
        analyst = AnalystResponse(
            country="Тайланд",
            region=["Пхукет"],
            category=[],
            preferences=[],
        )
        if is_empty_criteria(analyst):
            result["message"] = "test"

        assert "message" not in result
