"""Tests for API routes."""

from unittest.mock import patch

import pytest
from main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestChatEndpoint:
    """Tests for POST /api/chat endpoint."""

    def test_valid_request(self, client):
        """Valid request returns 200 with parsed JSON response."""
        with patch("api.routes.process_chat") as mock_process:
            mock_process.return_value = {
                "hotelList": [],
                "travelRecommendation": "test",
            }

            r = client.post(
                "/api/chat",
                json={"countryId": 1, "message": "test"},
            )
            assert r.status_code == 200
            data = r.get_json()
            assert data["countryId"] == 1
            assert data["status"] == "ok"
            assert "hotelList" in data["message"]

    def test_country_id_zero(self, client):
        """countryId=0 returns 422 with validation error."""
        r = client.post("/api/chat", json={"countryId": 0, "message": "test"})
        assert r.status_code == 422
        data = r.get_json()
        assert "countryId must be a positive integer" in data["error"]

    def test_country_id_negative(self, client):
        """countryId=-5 returns 422."""
        r = client.post("/api/chat", json={"countryId": -5, "message": "test"})
        assert r.status_code == 422
        data = r.get_json()
        assert "countryId must be a positive integer" in data["error"]

    def test_message_empty(self, client):
        """Empty message returns 422."""
        r = client.post("/api/chat", json={"countryId": 1, "message": ""})
        assert r.status_code == 422
        data = r.get_json()
        assert "message must not be empty" in data["error"]

    def test_message_too_long(self, client):
        """Message > 1000 chars returns 422."""
        r = client.post("/api/chat", json={"countryId": 1, "message": "x" * 1001})
        assert r.status_code == 422
        data = r.get_json()
        assert "message must not exceed 1000 characters" in data["error"]

    def test_message_whitespace(self, client):
        """Whitespace-only message returns 422."""
        r = client.post("/api/chat", json={"countryId": 1, "message": "   "})
        assert r.status_code == 422
        data = r.get_json()
        assert "message must not be empty" in data["error"]

    def test_country_not_found(self, client):
        """Invalid countryId returns 400."""
        with patch("api.routes.process_chat") as mock_process:
            mock_process.side_effect = ValueError("Country 99 not found")

            r = client.post("/api/chat", json={"countryId": 99, "message": "test"})
            assert r.status_code == 400
            data = r.get_json()
            assert data["message"]["error"] == "Country 99 not found"
