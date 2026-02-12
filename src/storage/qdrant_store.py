"""Qdrant Cloud vector store integration."""

# type: ignore  # Qdrant client library has complex type definitions

import asyncio
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from ..utils.logging import get_logger
from ..config import get_settings

logger = get_logger(__name__)


class QdrantStore:
    """Qdrant Cloud vector store manager."""

    def __init__(self) -> None:
        """Initialize Qdrant client."""
        settings = get_settings()
        self.client = None
        self.url = settings.qdrant_url
        self.api_key = settings.qdrant_api_key
        self.collection_name = settings.qdrant_collection_name
        self._initialized = False
        self._enabled = bool(self.url and self.api_key)

    async def initialize(self, vector_size: int = 768) -> None:
        """Initialize collection if it doesn't exist."""
        if self._initialized:
            return

        if not self._enabled:
            logger.warning("Qdrant not configured, skipping initialization")
            return

        try:
            # Create client with generous timeout for remote connections
            self.client = QdrantClient(
                url=self.url,
                api_key=self.api_key,
                timeout=300,
            )

            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if not exists:
                logger.info(f"Creating Qdrant collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                )

            self._initialized = True
            logger.info("Qdrant store initialized")
        except Exception as e:
            logger.error("Failed to initialize Qdrant", error=str(e))
            self._enabled = False

    async def insert_vectors(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
        batch_size: int = 64,
    ) -> None:
        """Insert vectors with metadata, batched to avoid timeouts."""
        if not self._enabled or not self.client:
            logger.warning("Qdrant not available, skipping insert")
            return

        try:
            if ids is None:
                import uuid

                ids = [str(uuid.uuid4()) for _ in range(len(vectors))]

            total = len(vectors)
            inserted = 0

            for i in range(0, total, batch_size):
                batch_ids = ids[i : i + batch_size]
                batch_vectors = vectors[i : i + batch_size]
                batch_payloads = payloads[i : i + batch_size]

                points = [
                    PointStruct(id=id_, vector=vector, payload=payload)
                    for id_, vector, payload in zip(batch_ids, batch_vectors, batch_payloads)
                ]

                # Retry with exponential backoff for transient failures
                for attempt in range(3):
                    try:
                        self.client.upsert(
                            collection_name=self.collection_name, points=points
                        )
                        break
                    except Exception as e:
                        if attempt < 2:
                            wait = 2 ** attempt
                            logger.warning(
                                f"Qdrant upsert attempt {attempt + 1} failed, retrying in {wait}s",
                                error=str(e),
                            )
                            await asyncio.sleep(wait)
                        else:
                            raise

                inserted += len(points)
                logger.info(f"Inserted batch {i // batch_size + 1} ({inserted}/{total} vectors)")

            logger.info(f"Inserted {total} vectors into Qdrant")
        except Exception as e:
            logger.error("Failed to insert vectors", error=str(e))
            raise

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors using the new query_points API.
        
        Note: Qdrant client v1.12+ replaced search() with query_points().
        See: https://qdrant.tech/blog/qdrant-1.10.x/
        """
        if not self._enabled or not self.client:
            logger.warning("Qdrant not available")
            return []

        try:
            query_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                if conditions:
                    query_filter = Filter(must=conditions)

            # Use new query_points API instead of deprecated search()
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,  # Changed from query_vector to query
                limit=top_k,
                query_filter=query_filter,
            )

            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload,
                }
                for hit in results.points  # Results are now in .points attribute
            ]
        except Exception as e:
            logger.error("Search failed", error=str(e))
            raise

    async def delete_by_filter(self, filters: Dict[str, Any]) -> None:
        """Delete vectors by filter."""
        try:
            conditions = []
            for key, value in filters.items():
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))

            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(must=conditions),
            )

            logger.info("Deleted vectors by filter")
        except Exception as e:
            logger.error("Failed to delete vectors", error=str(e))
            raise

    async def count(self) -> int:
        """Get total vector count."""
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count
        except Exception as e:
            logger.error("Failed to get count", error=str(e))
            return 0

    async def health_check(self) -> bool:
        """Check Qdrant connection health."""
        if not self._enabled or not self.client:
            return False

        try:
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error("Qdrant health check failed", error=str(e))
            return False
