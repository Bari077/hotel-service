"""Unit tests for cache module."""

import json
import os
import time

import pytest

from cache.cache import cache_get, cache_set, cache_delete, _make_key


class TestCacheKey:
    """Tests for cache key generation."""

    def test_key_is_deterministic(self):
        """Same parts produce the same key."""
        key1 = _make_key("a", "b", "c")
        key2 = _make_key("a", "b", "c")
        assert key1 == key2

    def test_key_contains_prefix(self):
        """Key starts with hotel:cache: prefix."""
        key = _make_key("test", "data")
        assert key.startswith("hotel:cache:")

    def test_key_is_short(self):
        """Key length is reasonable (≤ 1024 chars)."""
        key = _make_key("a" * 10000)
        assert len(key) <= 1024


class TestCacheOperations:
    """Tests for Redis cache operations."""

    def test_cache_set_and_get(self):
        """Set a value, then get it back."""
        key_parts = ("test", "key", "value")
        cache_set(key_parts, json.dumps({"data": "test_value"}), ttl=60)
        result = cache_get(key_parts)
        assert json.loads(result) == {"data": "test_value"}

    def test_cache_miss(self):
        """Nonexistent key returns None."""
        key_parts = ("nonexistent", "key", "12345")
        result = cache_get(key_parts)
        assert result is None

    def test_cache_ttl_from_env(self):
        """TTL is read from CACHE_TTL env variable."""
        key_parts = ("ttl", "test")
        cache_set(key_parts, json.dumps({"value": "test"}), ttl=30)
        result = cache_get(key_parts)
        assert json.loads(result) == {"value": "test"}

    def test_cache_overwrite(self):
        """Overwriting a key returns the new value."""
        key_parts = ("overwrite", "test")
        cache_set(key_parts, json.dumps({"v": "v1"}), ttl=60)
        cache_set(key_parts, json.dumps({"v": "v2"}), ttl=60)
        result = cache_get(key_parts)
        assert json.loads(result) == {"v": "v2"}


class TestCacheInvalidation:
    """Tests for invalid JSON handling."""

    def test_cache_set_rejects_invalid_json(self):
        """cache_set returns False for invalid JSON."""
        key_parts = ("invalid", "test")
        result = cache_set(key_parts, "not json", ttl=60)
        assert result is False

    def test_cache_delete(self):
        """cache_delete removes key from cache."""
        key_parts = ("delete", "test")
        cache_set(key_parts, json.dumps({"data": "value"}), ttl=60)
        cache_delete(key_parts)
        result = cache_get(key_parts)
        assert result is None
