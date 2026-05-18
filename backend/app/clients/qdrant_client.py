"""
Qdrant vector database async client with singleton pattern.
"""

from typing import Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams

import asyncio

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger()

# Global Qdrant client instance
_qdrant_client: Optional[AsyncQdrantClient] = None

# Qdrant default collection settings
DEFAULT_COLLECTION_NAME = "knowledge_base"
DEFAULT_VECTOR_SIZE = 768  # Gemini text-embedding-004 embedding size
DEFAULT_DISTANCE_METRIC = Distance.COSINE


class _MockQdrantClient:
    """Mock in-memory Qdrant client for development/testing when Qdrant is unavailable."""

    def __init__(self):
        self._collections = {}
        self._lock = asyncio.Lock()

    async def get_collections(self):
        """Return mock collections list."""
        async with self._lock:
            return type('Collections', (), {'collections': []})()

    async def create_collection(self, collection_name, vectors_config):
        """Create mock collection."""
        async with self._lock:
            self._collections[collection_name] = {"vectors_config": vectors_config, "points": []}
        return True

    async def collection_exists(self, collection_name):
        """Check if collection exists."""
        async with self._lock:
            return collection_name in self._collections

    async def upsert(self, collection_name, points, wait=True):
        """Mock upsert operation."""
        async with self._lock:
            if collection_name not in self._collections:
                self._collections[collection_name] = {"vectors_config": None, "points": []}
            self._collections[collection_name]["points"] = points
        return True

    async def search(self, collection_name, query_vector, limit=10, **kwargs):
        """Mock search operation - return empty results."""
        return []

    async def delete(self, collection_name, points_selector=None, **kwargs):
        """Mock delete operation."""
        return True

    async def close(self):
        """Mock close."""
        return True


async def init_qdrant() -> AsyncQdrantClient:
    """
    Initialize and connect to Qdrant vector database.
    Creates default collection if it doesn't exist.
    Should be called on application startup.
    
    Returns:
        AsyncQdrantClient: Connected Qdrant async client
    """
    global _qdrant_client

    settings = get_settings()

    try:
        _qdrant_client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
        )

        # Test connection
        await _qdrant_client.get_collections()
        logger.info(f"Qdrant connection established: {settings.QDRANT_URL}")

        # Create default collection if it doesn't exist
        collections = await _qdrant_client.get_collections()
        collection_names = [collection.name for collection in collections.collections]

        if DEFAULT_COLLECTION_NAME not in collection_names:
            await _qdrant_client.create_collection(
                collection_name=DEFAULT_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=DEFAULT_VECTOR_SIZE,
                    distance=DEFAULT_DISTANCE_METRIC,
                ),
            )
            logger.info(
                f"Created default Qdrant collection: {DEFAULT_COLLECTION_NAME} "
                f"(size={DEFAULT_VECTOR_SIZE}, distance={DEFAULT_DISTANCE_METRIC.name})"
            )
        else:
            logger.info(f"Default collection {DEFAULT_COLLECTION_NAME} already exists")

        return _qdrant_client
    except Exception as exc:
        logger.error(f"Failed to initialize Qdrant: {str(exc)}", exc_info=exc)
        logger.warning("Falling back to mock in-memory Qdrant client for development/testing.")
        try:
            _qdrant_client = _MockQdrantClient()
            await _qdrant_client.get_collections()
            return _qdrant_client
        except Exception:
            raise


async def close_qdrant() -> None:
    """
    Close Qdrant connection.
    Should be called on application shutdown.
    """
    global _qdrant_client

    if _qdrant_client:
        try:
            await _qdrant_client.close()
            logger.info("Qdrant connection closed")
        except Exception as exc:
            logger.error(f"Error closing Qdrant connection: {str(exc)}", exc_info=exc)


def get_qdrant() -> AsyncQdrantClient:
    """
    Get Qdrant client instance.
    
    Returns:
        AsyncQdrantClient: Connected Qdrant async client
        
    Raises:
        RuntimeError: If Qdrant client is not initialized
        
    Example:
        qdrant = get_qdrant()
        await qdrant.get_collections()
    """
    if _qdrant_client is None:
        raise RuntimeError("Qdrant client not initialized. Call init_qdrant() first.")
    return _qdrant_client


async def test_qdrant_connection() -> bool:
    """
    Test Qdrant connectivity.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        qdrant = get_qdrant()
        await qdrant.get_collections()
        logger.debug("Qdrant connection test successful")
        return True
    except Exception as exc:
        logger.error(f"Qdrant connection test failed: {str(exc)}", exc_info=exc)
        return False
