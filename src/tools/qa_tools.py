"""Q&A tools for natural language codebase querying."""

from typing import Dict, Any, Optional
from ..storage.storage_manager import StorageManager
from ..rag.pipeline import RAGPipeline
from ..utils.logging import get_logger

logger = get_logger(__name__)


class QATools:
    """Tools for Q&A on codebase."""

    def __init__(self, storage: StorageManager):
        """Initialize Q&A tools."""
        self.storage = storage
        self.rag = RAGPipeline(storage)

    async def ask_codebase(
        self,
        question: str,
        top_k: int = 5,
        language_filter: Optional[str] = None,
        project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Answer questions about the codebase."""
        try:
            return await self.rag.query(question, top_k, language_filter, project)
        except Exception as e:
            logger.error("Q&A failed", error=str(e))
            return {"success": False, "error": str(e)}
