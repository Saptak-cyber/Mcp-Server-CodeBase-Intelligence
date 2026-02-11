"""Code indexer for building search indices."""

from typing import List, Dict, Any
from .embeddings import EmbeddingGenerator
from .chunker import CodeChunker
from ..storage.qdrant_store import QdrantStore
from ..parsers.tree_sitter_manager import TreeSitterManager
from ..utils.logging import get_logger

logger = get_logger(__name__)


class CodeIndexer:
    """Index code for semantic search."""

    def __init__(self, qdrant: QdrantStore):
        """Initialize code indexer."""
        self.qdrant = qdrant
        self.embedder = EmbeddingGenerator()
        self.chunker = CodeChunker()
        self.parser = TreeSitterManager()

    async def index_file(
        self, file_path: str, code: str, language: str
    ) -> Dict[str, Any]:
        """Index a single file."""
        try:
            # Parse code
            tree = await self.parser.parse(code, language)

            # Chunk code
            chunks = await self.chunker.chunk_code(code, tree, file_path, language)

            if not chunks:
                return {"chunks_created": 0, "vectors_inserted": 0}

            # Generate embeddings
            texts = [chunk["code"] for chunk in chunks]
            vectors = await self.embedder.embed_batch(texts)

            # Prepare payloads
            payloads = [
                {
                    "file_path": chunk["file_path"],
                    "language": chunk["language"],
                    "chunk_type": chunk["chunk_type"],
                    "name": chunk.get("name", ""),
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "code": chunk["code"],
                }
                for chunk in chunks
            ]

            # Insert into Qdrant
            await self.qdrant.insert_vectors(vectors, payloads)

            return {
                "chunks_created": len(chunks),
                "vectors_inserted": len(vectors),
            }

        except Exception as e:
            logger.error(f"Failed to index {file_path}", error=str(e))
            return {"chunks_created": 0, "vectors_inserted": 0, "error": str(e)}

    async def remove_file_index(self, file_path: str) -> None:
        """Remove file from index."""
        await self.qdrant.delete_by_filter({"file_path": file_path})
        logger.info(f"Removed index for {file_path}")
