"""Upstash Redis caching layer."""

# type: ignore  # Upstash Redis library has incomplete type stubs

import json
import pickle
from typing import Any, Optional
from upstash_redis import Redis
from ..utils.logging import get_logger
from ..config import get_settings

logger = get_logger(__name__)


class UpstashCache:
    """Upstash Redis cache manager."""

    def __init__(self) -> None:
        """Initialize Upstash Redis client."""
        settings = get_settings()
        self.url = settings.upstash_redis_url
        self.token = settings.upstash_redis_token
        self.default_ttl = settings.cache_ttl_seconds
        self.enabled = settings.enable_caching and bool(self.url and self.token)
        self.client = None

        if self.enabled:
            try:
                self.client = Redis(url=self.url, token=self.token)
            except Exception as e:
                logger.warning("Failed to initialize Upstash Redis", error=str(e))
                self.enabled = False

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled or not self.client:
            return None

        try:
            value = self.client.get(key)
            if value is None:
                return None

            # Try to deserialize
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(value)
        except Exception as e:
            logger.warning(f"Cache get failed for key: {key}", error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL."""
        if not self.enabled or not self.client:
            return False

        try:
            ttl = ttl or self.default_ttl

            # Try to serialize as JSON first
            try:
                serialized = json.dumps(value)
            except (TypeError, ValueError):
                # Fall back to pickle for complex objects
                serialized = pickle.dumps(value)

            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for key: {key}", error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.enabled:
            return False

        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed for key: {key}", error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.enabled:
            return False

        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.warning(f"Cache exists check failed for key: {key}", error=str(e))
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.enabled:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                deleted = self.client.delete(*keys)
                logger.info(f"Cleared {deleted} cache keys matching: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.warning(f"Cache clear pattern failed: {pattern}", error=str(e))
            return 0

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter."""
        if not self.enabled:
            return 0

        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            logger.warning(f"Cache increment failed for key: {key}", error=str(e))
            return 0

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple keys at once."""
        if not self.enabled:
            return {}

        try:
            values = self.client.mget(keys)
            result = {}

            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        result[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        result[key] = pickle.loads(value)

            return result
        except Exception as e:
            logger.warning("Cache get_many failed", error=str(e))
            return {}

    async def set_many(self, items: dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple keys at once."""
        if not self.enabled:
            return False

        try:
            ttl = ttl or self.default_ttl

            # Use pipeline for efficiency
            pipeline = self.client.pipeline()

            for key, value in items.items():
                try:
                    serialized = json.dumps(value)
                except (TypeError, ValueError):
                    serialized = pickle.dumps(value)

                pipeline.setex(key, ttl, serialized)

            pipeline.execute()
            return True
        except Exception as e:
            logger.warning("Cache set_many failed", error=str(e))
            return False

    async def health_check(self) -> bool:
        """Check Redis connection health."""
        if not self.enabled or not self.client:
            return False

        try:
            self.client.ping()
            return True
        except Exception as e:
            logger.error("Upstash health check failed", error=str(e))
            return False

    def make_cache_key(self, *parts: str) -> str:
        """Create cache key from parts."""
        return ":".join(str(p) for p in parts)
