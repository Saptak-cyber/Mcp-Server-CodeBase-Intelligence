"""Code similarity detection."""

from typing import Dict, Any, List
from ..storage.storage_manager import StorageManager
from ..search.embeddings import EmbeddingGenerator
from ..utils.logging import get_logger

logger = get_logger(__name__)


class SimilarityDetector:
    """Detect similar and duplicate code."""

    def __init__(self, storage: StorageManager):
        """Initialize similarity detector."""
        self.storage = storage
        self.embedder = EmbeddingGenerator()

    async def detect_duplicates(
        self, path: str, similarity_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """Detect duplicate code in a codebase."""
        try:
            logger.info(f"Detecting duplicates in {path}")

            duplicate_groups = []

            # Get all indexed code chunks for this path
            # Query Qdrant for chunks
            results = await self.storage.qdrant.search(
                query_vector=[0.0] * 768,  # Dummy vector, we'll compare all
                top_k=1000,
            )

            # Group similar chunks
            for i, chunk1 in enumerate(results):
                if i >= len(results) - 1:
                    break

                similar_chunks = [chunk1]

                for chunk2 in results[i + 1 :]:
                    # Calculate similarity (simplified - using score from Qdrant)
                    if chunk1["payload"]["file_path"] != chunk2["payload"]["file_path"]:
                        # Search for similarity
                        similar = await self._check_similarity(
                            chunk1["payload"]["code"],
                            chunk2["payload"]["code"],
                            similarity_threshold,
                        )

                        if similar:
                            similar_chunks.append(chunk2)

                if len(similar_chunks) > 1:
                    duplicate_groups.append(
                        {
                            "code_sample": chunk1["payload"]["code"][:200],
                            "instances": [
                                {
                                    "file": c["payload"]["file_path"],
                                    "lines": f"{c['payload']['start_line']}-{c['payload']['end_line']}",
                                }
                                for c in similar_chunks
                            ],
                            "similarity_score": similarity_threshold,
                        }
                    )

                    # Limit to first 10 groups
                    if len(duplicate_groups) >= 10:
                        break

            return {
                "success": True,
                "path": path,
                "duplicate_groups_found": len(duplicate_groups),
                "duplicates": duplicate_groups,
            }

        except Exception as e:
            logger.error("Duplicate detection failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def _check_similarity(
        self, code1: str, code2: str, threshold: float
    ) -> bool:
        """Check if two code snippets are similar."""
        try:
            # Generate embeddings
            emb1 = await self.embedder.embed(code1)
            emb2 = await self.embedder.embed(code2)

            # Calculate cosine similarity
            similarity = self._cosine_similarity(emb1, emb2)

            return similarity >= threshold

        except Exception:
            return False

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between vectors."""
        import math

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)
