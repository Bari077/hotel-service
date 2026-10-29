"""Redis cache implementation with TTL."""

import hashlib
import json
import logging
import os
from typing import Any

import redis

logger = logging.getLogger("hotel-service")

_redis_client: redis.Redis | None = None


def _get_redis() -> redis.Redis:
    """Lazy-init Redis client from env."""
    global _redis_client
    if _redis_client is None:
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = redis.from_url(url, decode_responses=True)
    return _redis_client


def _make_key(*parts: str) -> str:
    """Create a Redis key from hash of all parts (key name can't exceed 1024 bytes)."""
    raw = "|".join(parts)
    return f"hotel:cache:{hashlib.sha256(raw.encode()).hexdigest()[:32]}"


def cache_get(key_parts: tuple[str, ...]) -> str | None:
    """Get cached value. Logs HIT/MISS."""
    key = _make_key(*key_parts)
    r = _get_redis()
    value = r.get(key)
    if value is not None:
        logger.info("CACHE HIT  key=%s", key[:40])
        return value
    logger.info("CACHE MISS key=%s", key[:40])
    return None


def cache_set(key_parts: tuple[str, ...], value: str, ttl: int | None = None) -> None:
    """Store value with TTL. Logs the set."""
    key = _make_key(*key_parts)
    r = _get_redis()
    ttl = ttl or int(os.getenv("CACHE_TTL", 600))  # default 10 min
    r.set(key, value, ex=ttl)
    logger.info("CACHE SET  key=%s ttl=%ds", key[:40], ttl)
