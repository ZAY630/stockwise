"""TTL-based in-memory cache for external API responses."""

import asyncio
import functools
import hashlib
import json
import time
from typing import Any, Callable

from app.config import settings


class TTLCache:
    """Simple TTL-based in-memory cache."""

    def __init__(self, ttl_seconds: int = 300):
        self._cache: dict[str, tuple[float, Any]] = {}
        self._ttl = ttl_seconds
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        """Get a value from cache, returning None if expired or missing."""
        async with self._lock:
            if key in self._cache:
                expiry, value = self._cache[key]
                if time.time() < expiry:
                    return value
                    # Expired — clean up
                del self._cache[key]
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Store a value in the cache."""
        ttl = ttl_seconds if ttl_seconds is not None else self._ttl
        async with self._lock:
            self._cache[key] = (time.time() + ttl, value)

    async def clear(self) -> None:
        """Clear all cached entries."""
        async with self._lock:
            self._cache.clear()

    def make_key(self, *args, **kwargs) -> str:
        """Create a deterministic cache key from function arguments."""
        raw = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


# Global cache instance
cache = TTLCache(ttl_seconds=settings.CACHE_TTL_SECONDS)


def ttl_cache(ttl_seconds: int | None = None):
    """Decorator for async functions to cache their results with TTL."""

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = cache.make_key(func.__name__, *args, **kwargs)
            cached = await cache.get(key)
            if cached is not None:
                return cached
            result = await func(*args, **kwargs)
            await cache.set(key, result, ttl_seconds)
            return result

        return wrapper

    return decorator
