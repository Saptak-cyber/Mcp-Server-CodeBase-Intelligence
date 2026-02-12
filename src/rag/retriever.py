"""Context retriever for RAG."""

from typing import List, Dict, Any, Optional
from ..storage.storage_manager import StorageManager
from ..search.embeddings import EmbeddingGenerator
from ..utils.logging import get_logger

logger = get_logger(__name__)


class ContextRetriever:
    """Retrieve relevant code context for questions."""

    def __init__(self, storage: StorageManager):
        """Initialize context retriever."""
        self.storage = storage
        self.embedder = EmbeddingGenerator()

    async def retrieve(
        self,
        question: str,
        top_k: int = 5,
        language_filter: Optional[str] = None,
        project: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant code contexts."""
        # Generate question embedding
        question_embedding = await self.embedder.embed(question)

        # Build filters
        filters = {}
        if language_filter:
            filters["language"] = language_filter
        if project:
            filters["project"] = project

        # Search in Qdrant
        results = await self.storage.qdrant.search(
            query_vector=question_embedding,
            top_k=top_k,
            filters=filters,
        )

        # Format contexts
        contexts = [
            {
                "file_path": r["payload"]["file_path"],
                "language": r["payload"]["language"],
                "project": r["payload"].get("project", "unknown"),
                "type": r["payload"]["chunk_type"],
                "name": r["payload"].get("name", ""),
                "lines": f"{r['payload']['start_line']}-{r['payload']['end_line']}",
                "code": r["payload"]["code"],
                "relevance_score": round(r["score"], 4),
            }
            for r in results
        ]

        return contexts
