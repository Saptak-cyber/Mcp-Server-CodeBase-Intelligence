"""RAG pipeline for codebase Q&A."""

from typing import Dict, Any, Optional
from ..storage.storage_manager import StorageManager
from .retriever import ContextRetriever
from .context_formatter import ContextFormatter
from ..utils.logging import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline."""

    def __init__(self, storage: StorageManager):
        """Initialize RAG pipeline."""
        self.storage = storage
        self.retriever = ContextRetriever(storage)
        self.formatter = ContextFormatter()

    async def query(
        self,
        question: str,
        top_k: int = 5,
        language_filter: Optional[str] = None,
        project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Query the codebase with natural language."""
        try:
            logger.info(f"RAG query: {question}")

            # Retrieve relevant context
            contexts = await self.retriever.retrieve(question, top_k, language_filter, project)

            # Format response
            formatted_response = await self.formatter.format(question, contexts)

            return {
                "success": True,
                "question": question,
                "contexts_retrieved": len(contexts),
                "response": formatted_response,
                "relevant_code": contexts,
            }

        except Exception as e:
            logger.error("RAG query failed", error=str(e))
            return {"success": False, "error": str(e)}
