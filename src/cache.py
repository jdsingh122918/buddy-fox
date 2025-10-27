"""
Caching system for web search and fetch results.
Reduces API costs and improves response times for repeated queries.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

from .logging_config import get_logger

# Get logger for cache module
_logger = get_logger(__name__)


@dataclass
class CacheEntry:
    """A cached result entry."""

    key: str
    value: Any
    created_at: float
    expires_at: float
    hit_count: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() > self.expires_at

    def is_valid(self) -> bool:
        """Check if cache entry is valid (not expired)."""
        return not self.is_expired()

    def increment_hits(self) -> None:
        """Increment hit counter."""
        self.hit_count += 1

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "hit_count": self.hit_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CacheEntry":
        """Create from dictionary."""
        return cls(**data)


class ResultCache:
    """
    Simple in-memory cache for web search and fetch results.

    Features:
    - TTL-based expiration
    - LRU eviction when max size reached
    - Optional persistence to disk
    - Hit/miss statistics
    """

    def __init__(
        self,
        max_size: int = 100,
        default_ttl: int = 3600,  # 1 hour
        persist_path: Optional[Path] = None,
    ):
        """
        Initialize the cache.

        Args:
            max_size: Maximum number of entries to store
            default_ttl: Default time-to-live in seconds
            persist_path: Optional path to persist cache to disk
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.persist_path = persist_path
        self._cache: dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0

        # Load from disk if persistence is enabled
        if self.persist_path and self.persist_path.exists():
            self._load()

    def _make_key(self, prefix: str, data: dict) -> str:
        """
        Create a cache key from prefix and data.

        Args:
            prefix: Key prefix (e.g., 'search', 'fetch')
            data: Data to hash

        Returns:
            str: Cache key
        """
        # Sort dict keys for consistent hashing
        serialized = json.dumps(data, sort_keys=True)
        hash_hex = hashlib.sha256(serialized.encode()).hexdigest()[:16]
        return f"{prefix}:{hash_hex}"

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        entry = self._cache.get(key)

        if entry is None:
            self._misses += 1
            _logger.log_cache_event("miss", key, reason="not_found")
            return None

        if entry.is_expired():
            del self._cache[key]
            self._misses += 1
            _logger.log_cache_event("miss", key, reason="expired")
            return None

        entry.increment_hits()
        self._hits += 1
        _logger.log_cache_event("hit", key, hit_count=entry.hit_count)
        return entry.value

    def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default)
        """
        ttl = ttl if ttl is not None else self.default_ttl
        now = time.time()

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            expires_at=now + ttl,
        )

        # Evict oldest entry if cache is full
        evicted = False
        if len(self._cache) >= self.max_size:
            self._evict_oldest()
            evicted = True

        self._cache[key] = entry

        # Log cache set
        _logger.log_cache_event(
            "set",
            key,
            ttl_seconds=ttl,
            cache_size=len(self._cache),
            evicted=evicted,
        )

        # Persist if enabled
        if self.persist_path:
            self._save()

    def _evict_oldest(self) -> None:
        """Evict the oldest (least recently created) entry."""
        if not self._cache:
            return

        oldest_key = min(
            self._cache.keys(), key=lambda k: self._cache[k].created_at
        )
        del self._cache[oldest_key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

        if self.persist_path and self.persist_path.exists():
            self.persist_path.unlink()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }

    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns number of entries removed."""
        expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)

    def _save(self) -> None:
        """Save cache to disk."""
        if not self.persist_path:
            return

        self.persist_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "entries": [entry.to_dict() for entry in self._cache.values()],
            "hits": self._hits,
            "misses": self._misses,
        }

        with open(self.persist_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load(self) -> None:
        """Load cache from disk."""
        if not self.persist_path or not self.persist_path.exists():
            return

        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            self._cache = {
                entry["key"]: CacheEntry.from_dict(entry)
                for entry in data.get("entries", [])
                if not CacheEntry.from_dict(entry).is_expired()
            }

            self._hits = data.get("hits", 0)
            self._misses = data.get("misses", 0)

        except Exception as e:
            # If loading fails, start fresh
            self._cache.clear()
            self._hits = 0
            self._misses = 0


class SearchCache:
    """
    Specialized cache for web search results.
    """

    def __init__(self, cache: Optional[ResultCache] = None):
        """
        Initialize search cache.

        Args:
            cache: Optional ResultCache instance to use
        """
        self.cache = cache or ResultCache(default_ttl=1800)  # 30 minutes

    def get_search(self, query: str, **kwargs) -> Optional[Any]:
        """Get cached search results."""
        key_data = {"query": query, **kwargs}
        key = self.cache._make_key("search", key_data)
        return self.cache.get(key)

    def set_search(self, query: str, results: Any, ttl: Optional[int] = None, **kwargs) -> None:
        """Cache search results."""
        key_data = {"query": query, **kwargs}
        key = self.cache._make_key("search", key_data)
        self.cache.set(key, results, ttl)


class FetchCache:
    """
    Specialized cache for web fetch results.
    """

    def __init__(self, cache: Optional[ResultCache] = None):
        """
        Initialize fetch cache.

        Args:
            cache: Optional ResultCache instance to use
        """
        self.cache = cache or ResultCache(default_ttl=3600)  # 1 hour

    def get_fetch(self, url: str, prompt: Optional[str] = None) -> Optional[Any]:
        """Get cached fetch results."""
        key_data = {"url": url}
        if prompt:
            key_data["prompt"] = prompt
        key = self.cache._make_key("fetch", key_data)
        return self.cache.get(key)

    def set_fetch(
        self, url: str, results: Any, ttl: Optional[int] = None, prompt: Optional[str] = None
    ) -> None:
        """Cache fetch results."""
        key_data = {"url": url}
        if prompt:
            key_data["prompt"] = prompt
        key = self.cache._make_key("fetch", key_data)
        self.cache.set(key, results, ttl)


# Global cache instances
_global_cache: Optional[ResultCache] = None


def get_global_cache(
    max_size: int = 100,
    default_ttl: int = 3600,
    persist: bool = False,
) -> ResultCache:
    """
    Get or create the global cache instance.

    Args:
        max_size: Maximum cache size
        default_ttl: Default TTL in seconds
        persist: Whether to persist cache to disk

    Returns:
        ResultCache: Global cache instance
    """
    global _global_cache

    if _global_cache is None:
        persist_path = None
        if persist:
            persist_path = Path.home() / ".cache" / "buddy-fox" / "results.json"

        _global_cache = ResultCache(
            max_size=max_size,
            default_ttl=default_ttl,
            persist_path=persist_path,
        )

    return _global_cache


def clear_global_cache() -> None:
    """Clear the global cache."""
    global _global_cache
    if _global_cache:
        _global_cache.clear()
    _global_cache = None
