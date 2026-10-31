"""Unit tests for business logic."""

import pytest

from services.service import process_chat, is_empty_criteria
from llm.schemas import AnalystResponse


class TestProcessChat:
    """Tests for process_chat function."""

    def test_process_chat_no_auth_key(self, monkeypatch):
        """Missing LLM_AUTH_KEY raises RuntimeError."""
        monkeypatch.delenv("LLM_AUTH_KEY", raising=False)
        with pytest.raises(RuntimeError, match="Сервис временно недоступен"):
            process_chat("test")


class TestIsEmptyCriteria:
    """Tests for is_empty_criteria function."""

    def test_all_empty(self):
        """All criteria empty → True."""
        analyst = AnalystResponse(
            country="Тайланд",
            locations=[],
            category=[],
            preferences=[],
        )
        assert is_empty_criteria(analyst) is True

    def test_locations_present(self):
        """Locations specified → False."""
        analyst = AnalystResponse(
            country="Тайланд",
            locations=["Пхукет"],
            category=[],
            preferences=[],
        )
        assert is_empty_criteria(analyst) is False

    def test_category_present(self):
        """Category specified → False."""
        analyst = AnalystResponse(
            country="Тайланд",
            locations=[],
            category=[5],
            preferences=[],
        )
        assert is_empty_criteria(analyst) is False

    def test_preferences_present(self):
        """Preferences specified → False."""
        analyst = AnalystResponse(
            country="Тайланд",
            locations=[],
            category=[],
            preferences=["у моря"],
        )
        assert is_empty_criteria(analyst) is False

    def test_all_present(self):
        """All criteria specified → False."""
        analyst = AnalystResponse(
            country="Тайланд",
            locations=["Пхукет"],
            category=[5],
            preferences=["все включено"],
        )
        assert is_empty_criteria(analyst) is False
