"""
Redis async client with singleton pattern and connection pooling.
"""

from typing import Optional
import redis.asyncio as aioredis
import asyncio
from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger()

# Global Redis client instance
_redis_client: Optional[Redis] = None


class _InMemoryRedis:
    """Simple async in-memory Redis-like fallback for local testing."""

    def __init__(self):
        self._store = {}
        self._lock = asyncio.Lock()

    async def ping(self):
        return True

    async def get(self, key: str):
        async with self._lock:
            return self._store.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None):
        async with self._lock:
            self._store[key] = value
            return True

    async def delete(self, key: str):
        async with self._lock:
            return self._store.pop(key, None) is not None

    async def keys(self, pattern: str):
        prefix = pattern.rstrip("*")
        async with self._lock:
            return [k for k in self._store.keys() if k.startswith(prefix)]

    async def close(self):
        return True


async def init_redis() -> Redis:
    """
    Initialize and connect to Redis.
    Should be called on application startup.
    
    Returns:
        Redis: Connected Redis async client
    """
    global _redis_client

    settings = get_settings()

    try:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf8",
            decode_responses=True,
        )

        # Test connection
        await _redis_client.ping()
        logger.info(f"Redis connection established: {settings.REDIS_URL}")
        return _redis_client
    except Exception as exc:
        logger.error(f"Failed to connect to Redis: {str(exc)}", exc_info=exc)
        logger.warning("Falling back to in-memory conversation store for development/testing.")
        # Use in-memory fallback that exposes async get/set/delete/keys/ping/close
        try:
            _redis_client = _InMemoryRedis()
            await _redis_client.ping()
            return _redis_client
        except Exception:
            raise


async def close_redis() -> None:
    """
    Close Redis connection.
    Should be called on application shutdown.
    """
    global _redis_client

    if _redis_client:
        try:
            await _redis_client.close()
            logger.info("Redis connection closed")
        except Exception as exc:
            logger.error(f"Error closing Redis connection: {str(exc)}", exc_info=exc)


def get_redis() -> Redis:
    """
    Get Redis client instance.
    
    Returns:
        Redis: Connected Redis async client
        
    Raises:
        RuntimeError: If Redis client is not initialized
        
    Example:
        redis = get_redis()
        await redis.set("key", "value")
    """
    if _redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() first.")
    return _redis_client


async def test_redis_connection() -> bool:
    """
    Test Redis connectivity.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        redis = get_redis()
        await redis.ping()
        logger.debug("Redis connection test successful")
        return True
    except Exception as exc:
        logger.error(f"Redis connection test failed: {str(exc)}", exc_info=exc)
        return False
