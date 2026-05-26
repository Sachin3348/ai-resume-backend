"""
Redis caching layer:
- Exact-match cache (SHA-256 hash) for /parse-resume
- Semantic LLM cache for /optimize-experience

Architecture:
- Main Redis client  → any DB (default: 0), exact-match only
- Semantic Redis     → ALWAYS DB 0 (RediSearch requirement)
- Embedding model   → singleton, loaded once per process
- Both clients use a _FAILED sentinel so init is never retried after failure
"""

import hashlib
import logging
import os
import re
from typing import Any

import redis
from app.config import get_settings

logger = logging.getLogger(__name__)

# Sentinel: distinguishes "not yet initialized" from "init was attempted and failed"
_FAILED = object()

# ---------------------------------------------------------------------------
# Singleton: Standard Redis client (exact-match cache)
# ---------------------------------------------------------------------------

_redis_client: Any = None  # None | redis.Redis | _FAILED


def _force_db0_url(url: str) -> str:
    """
    Rewrite a redis:// URL to always use DB 0.
    redis://host:port/N  →  redis://host:port/0
    redis://host:port    →  unchanged (already defaults to 0)
    """
    return re.sub(r"(redis://[^/]+)/\d+$", r"\1/0", url)


def get_redis() -> redis.Redis | None:
    """Lazy singleton — exact-match Redis. Returns None if unavailable."""
    global _redis_client
    if _redis_client is _FAILED:
        return None
    if _redis_client is not None:
        return _redis_client  # type: ignore[return-value]

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
        logger.warning("Redis unavailable (exact cache disabled): %s", exc)
        _redis_client = _FAILED
        return None


# ---------------------------------------------------------------------------
# Singleton: HuggingFace embedding model (sentence-transformers)
# Loaded once per process — never inside request handlers.
# ---------------------------------------------------------------------------

_embedding_model: Any = None  # None | model instance | _FAILED


def get_embedding_model():
    """
    Singleton sentence-transformers model used by the semantic cache.
    Loads weights exactly once per process lifetime.
    """
    global _embedding_model
    if _embedding_model is _FAILED:
        return None
    if _embedding_model is not None:
        return _embedding_model

    try:
        from sentence_transformers import SentenceTransformer

        settings = get_settings()
        if settings.hf_token:
            # Set for both sentence-transformers and redisvl's internal HF calls
            os.environ["HUGGINGFACEHUB_API_TOKEN"] = settings.hf_token
            os.environ["HF_TOKEN"] = settings.hf_token
            logger.info("HuggingFace token configured.")

        logger.info("Loading embedding model (once per process)…")
        _embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            token=settings.hf_token or None,
        )
        logger.info("Embedding model loaded: all-MiniLM-L6-v2")
        return _embedding_model
    except Exception as exc:
        logger.warning("Embedding model unavailable (semantic cache disabled): %s", exc)
        _embedding_model = _FAILED
        return None


# ---------------------------------------------------------------------------
# Singleton: Semantic Cache (redisvl)
# MUST use DB 0 — RediSearch does not support other DBs.
# ---------------------------------------------------------------------------

_semantic_cache: Any = None  # None | SemanticCache | _FAILED


def get_semantic_cache():
    """
    Lazy singleton SemanticCache.

    Guarantees:
    - init attempted exactly ONCE per process (sentinel pattern)
    - always connects to DB 0 (RediSearch requirement)
    - duplicate index creation is silently ignored
    - embedding model reused from singleton, never reloaded
    """
    global _semantic_cache
    if _semantic_cache is _FAILED:
        return None
    if _semantic_cache is not None:
        return _semantic_cache

    # Embedding model must be available first
    if get_embedding_model() is None:
        logger.warning("Semantic cache disabled: embedding model not available")
        _semantic_cache = _FAILED
        return None

    settings = get_settings()

    # RediSearch only works on DB 0 — enforce regardless of env var value
    semantic_url = _force_db0_url(settings.redis_semantic_url)
    if semantic_url != settings.redis_semantic_url:
        logger.warning(
            "redis_semantic_url was pointing to non-0 DB (%s). "
            "Forced to DB 0 (%s) — RediSearch requires DB 0.",
            settings.redis_semantic_url,
            semantic_url,
        )

    try:
        from redisvl.extensions.llmcache import SemanticCache

        _semantic_cache = SemanticCache(
            name="bullet_opt_cache",
            redis_url=semantic_url,
            distance_threshold=settings.semantic_distance_threshold,
            ttl=settings.cache_ttl_days * 86400,
        )
        logger.info(
            "Semantic cache initialized — Redis DB 0, threshold=%.2f, ttl=%dd",
            settings.semantic_distance_threshold,
            settings.cache_ttl_days,
        )
        return _semantic_cache
    except Exception as exc:
        # "Index already exists" is safe to ignore — happens on restart
        err = str(exc)
        if "already exists" in err.lower():
            logger.info("Semantic cache index already exists — reusing.")
            # Re-attempt without recreating index
            try:
                from redisvl.extensions.llmcache import SemanticCache
                _semantic_cache = SemanticCache(
                    name="bullet_opt_cache",
                    redis_url=semantic_url,
                    distance_threshold=settings.semantic_distance_threshold,
                    ttl=settings.cache_ttl_days * 86400,
                )
                return _semantic_cache
            except Exception as inner:
                logger.warning("SemanticCache reuse failed: %s", inner)

        logger.warning("SemanticCache unavailable, falling back to LLM: %s", exc)
        _semantic_cache = _FAILED
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
    """Set value in exact-match cache with optional TTL."""
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


# ---------------------------------------------------------------------------
# Startup: warm up singletons once at boot (called from main.py)
# ---------------------------------------------------------------------------

def warm_up_cache() -> None:
    """
    Pre-initialize all cache singletons at application startup.
    Prevents cold-start latency and repeated init attempts on first requests.
    """
    logger.info("Warming up cache singletons…")
    get_redis()
    get_embedding_model()   # loads weights once here, not on first request
    get_semantic_cache()
    logger.info("Cache warm-up complete.")
