"""Semantic search engine."""

from typing import List, Dict, Any, Optional
from .embeddings import EmbeddingGenerator
from ..storage.qdrant_store import QdrantStore
from ..utils.logging import get_logger

logger = get_logger(__name__)


class SemanticSearchEngine:
    """Semantic search engine using vector similarity."""

    def __init__(self, qdrant: QdrantStore):
        """Initialize semantic search engine."""
        self.qdrant = qdrant
        self.embedder = EmbeddingGenerator()

    async def search(
        self,
        query: str,
        top_k: int = 10,
        language_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search code semantically."""
        # Generate query embedding
        query_embedding = await self.embedder.embed(query)

        # Build filters
        filters = {}
        if language_filter:
            filters["language"] = language_filter

        # Search in Qdrant
        results = await self.qdrant.search(
            query_vector=query_embedding,
            top_k=top_k,
            filters=filters,
        )

        return results

    async def search_similar_code(
        self, code: str, top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Find similar code snippets."""
        code_embedding = await self.embedder.embed(code)

        results = await self.qdrant.search(
            query_vector=code_embedding,
            top_k=top_k,
        )

        return results
