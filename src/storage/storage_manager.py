"""Unified storage manager for all cloud services."""

from typing import Optional
from .qdrant_store import QdrantStore
from .neo4j_store import Neo4jStore
from .neon_store import NeonStore
from .upstash_cache import UpstashCache
from ..utils.logging import get_logger

logger = get_logger(__name__)


class StorageManager:
    """Unified manager for all storage services."""

    _instance: Optional["StorageManager"] = None

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize all storage clients."""
        if hasattr(self, "_initialized"):
            return

        self.qdrant = QdrantStore()
        self.neo4j = Neo4jStore()
        self.neon = NeonStore()
        self.cache = UpstashCache()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize all storage services."""
        if self._initialized:
            return

        logger.info("Initializing storage services...")

        # Initialize Qdrant (non-blocking)
        try:
            await self.qdrant.initialize()
        except Exception as e:
            logger.warning("Qdrant initialization failed", error=str(e))

        # Connect to Neo4j (non-blocking)
        try:
            await self.neo4j.connect()
        except Exception as e:
            logger.warning("Neo4j connection failed", error=str(e))

        # Initialize Neon (non-blocking)
        try:
            await self.neon.initialize()
        except Exception as e:
            logger.warning("Neon initialization failed", error=str(e))

        self._initialized = True
        logger.info("Storage initialization completed")

    async def close(self) -> None:
        """Close all storage connections."""
        try:
            await self.neo4j.close()
            await self.neon.close()
            logger.info("All storage connections closed")
        except Exception as e:
            logger.error("Error closing storage connections", error=str(e))

    async def health_check(self) -> dict[str, bool]:
        """Check health of all storage services."""
        return {
            "qdrant": await self.qdrant.health_check(),
            "neo4j": await self.neo4j.health_check(),
            "neon": await self.neon.health_check(),
            "upstash": await self.cache.health_check(),
        }

    async def clear_cache(self) -> None:
        """Clear all cached data."""
        await self.cache.clear_pattern("*")
        logger.info("Cache cleared")


# Global storage manager instance
_storage_manager: Optional[StorageManager] = None


def get_storage_manager() -> StorageManager:
    """Get or create the global storage manager."""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager()
    return _storage_manager
