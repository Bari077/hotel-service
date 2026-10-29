"""Tests for JSON parser utility."""

from utils.json_parser import extract_json


class TestExtractJson:
    """Tests for JSON extraction from LLM responses."""

    def test_valid_json(self):
        """Valid JSON is returned as-is."""
        text = '{"key": "value"}'
        assert extract_json(text) == text

    def test_malformed_nested_json(self):
        """Malformed nested JSON — extracts outermost valid object."""
        text = '{"hotelList": [{"region": "Дубай"}], "broken": "value"}'
        assert extract_json(text) == text

    def test_json_with_trailing_text(self):
        """JSON followed by extra text — extracts only JSON."""
        text = '{"key": "value"} some trailing text'
        assert extract_json(text) == '{"key": "value"}'

    def test_json_with_leading_text(self):
        """JSON preceded by extra text — extracts only JSON."""
        text = 'some leading text {"key": "value"}'
        assert extract_json(text) == '{"key": "value"}'

    def test_nested_json_in_string_value(self):
        """Nested JSON inside a string value — extracts outermost."""
        text = '{"region": "Фуджейра", "hotels": "{\\"hotelList\\": []}"}'
        result = extract_json(text)
        assert result is not None
        assert "region" in result

    def test_no_json_found(self):
        """No JSON in text — returns None."""
        assert extract_json("just plain text") is None

    def test_empty_string(self):
        """Empty string — returns None."""
        assert extract_json("") is None

    def test_only_braces(self):
        """Only opening brace — returns None."""
        assert extract_json("{") is None

    def test_deeply_nested_valid(self):
        """Deeply nested valid JSON — extracted correctly."""
        text = '{"a": {"b": {"c": {"d": "value"}}}}'
        assert extract_json(text) == text
