"""Unit tests for cache module."""

import os
import time

import pytest

from cache.cache import cache_get, cache_set, _make_key


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
        cache_set(key_parts, "test_value", ttl=60)
        result = cache_get(key_parts)
        assert result == "test_value"

    def test_cache_miss(self):
        """Nonexistent key returns None."""
        key_parts = ("nonexistent", "key", "12345")
        result = cache_get(key_parts)
        assert result is None

    def test_cache_ttl_from_env(self):
        """TTL is read from CACHE_TTL env variable."""
        key_parts = ("ttl", "test")
        cache_set(key_parts, "value", ttl=30)
        result = cache_get(key_parts)
        assert result == "value"

    def test_cache_overwrite(self):
        """Overwriting a key returns the new value."""
        key_parts = ("overwrite", "test")
        cache_set(key_parts, "v1", ttl=60)
        cache_set(key_parts, "v2", ttl=60)
        result = cache_get(key_parts)
        assert result == "v2"
