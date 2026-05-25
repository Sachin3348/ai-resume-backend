"""
Redis caching layer:
- Exact-match cache (SHA-256 hash) for /parse-resume
- Semantic LLM cache for /optimize-experience
"""

import hashlib
import json
import logging
from typing import Any

import redis
from app.config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Standard Redis client (exact-match cache)
# ---------------------------------------------------------------------------

_redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis | None:
    """Lazy singleton Redis connection. Returns None if connection fails."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    settings = get_settings()
    try:
        _redis_client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        _redis_client.ping()
        logger.info("Redis exact-cache connected: %s", settings.redis_url)
        return _redis_client
    except (redis.ConnectionError, redis.TimeoutError) as exc:
        logger.warning("Redis unavailable, falling back to LLM: %s", exc)
        _redis_client = None
        return None


# ---------------------------------------------------------------------------
# Semantic Cache (redisvl)
# ---------------------------------------------------------------------------

_semantic_cache: Any = None


def get_semantic_cache():
    """Lazy singleton SemanticCache. Returns None if unavailable."""
    global _semantic_cache
    if _semantic_cache is not None:
        return _semantic_cache

    settings = get_settings()
    try:
        from redisvl.extensions.llmcache import SemanticCache

        _semantic_cache = SemanticCache(
            name="bullet_opt_cache",
            redis_url=settings.redis_semantic_url,
            distance_threshold=settings.semantic_distance_threshold,
            ttl=settings.cache_ttl_days * 86400,
        )
        logger.info("Semantic cache initialized (threshold=%.2f)", settings.semantic_distance_threshold)
        return _semantic_cache
    except Exception as exc:
        logger.warning("SemanticCache unavailable, falling back to LLM: %s", exc)
        _semantic_cache = None
        return None


# ---------------------------------------------------------------------------
# Exact-Match Helpers
# ---------------------------------------------------------------------------


def hash_text(text: str) -> str:
    """SHA-256 hash of input text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def cache_get(key: str) -> str | None:
    """Get value from exact-match cache. Returns None on miss or error."""
    r = get_redis()
    if r is None:
        return None
    try:
        return r.get(key)
    except (redis.ConnectionError, redis.TimeoutError):
        logger.warning("Redis GET failed for key=%s", key[:16])
        return None


def cache_set(key: str, value: str, ttl_seconds: int | None = None) -> None:
    """Set value in exact-match cache with TTL."""
    r = get_redis()
    if r is None:
        return
    if ttl_seconds is None:
        ttl_seconds = get_settings().cache_ttl_days * 86400
    try:
        r.setex(key, ttl_seconds, value)
    except (redis.ConnectionError, redis.TimeoutError):
        logger.warning("Redis SETEX failed for key=%s", key[:16])


# ---------------------------------------------------------------------------
# Semantic Cache Helpers
# ---------------------------------------------------------------------------


def semantic_check(prompt: str) -> str | None:
    """Check semantic cache for a similar prompt. Returns cached response or None."""
    sc = get_semantic_cache()
    if sc is None:
        return None
    try:
        results = sc.check(prompt=prompt)
        if results:
            return results[0]["response"]
    except Exception as exc:
        logger.warning("SemanticCache check failed: %s", exc)
    return None


def semantic_store(prompt: str, response: str) -> None:
    """Store a prompt-response pair in semantic cache."""
    sc = get_semantic_cache()
    if sc is None:
        return
    try:
        sc.store(prompt=prompt, response=response)
    except Exception as exc:
        logger.warning("SemanticCache store failed: %s", exc)
