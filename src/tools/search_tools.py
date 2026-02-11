"""Search tools for code querying."""

from typing import Dict, Any, Optional, List
from ..storage.storage_manager import StorageManager
from ..search.embeddings import EmbeddingGenerator
from ..utils.logging import get_logger

logger = get_logger(__name__)


class SearchTools:
    """Tools for searching code."""

    def __init__(self, storage: StorageManager):
        """Initialize search tools."""
        self.storage = storage
        self.embedder = EmbeddingGenerator()

    async def semantic_search(
        self,
        query: str,
        language_filter: Optional[str] = None,
        top_k: int = 10,
    ) -> Dict[str, Any]:
        """Perform semantic search on codebase."""
        try:
            # Check cache first
            cache_key = self.storage.cache.make_cache_key(
                "search", query, language_filter or "all", str(top_k)
            )
            cached = await self.storage.cache.get(cache_key)
            if cached:
                logger.info("Returning cached search results")
                return cached

            # Generate query embedding
            query_vector = await self.embedder.embed(query)

            # Build filters
            filters = {}
            if language_filter:
                filters["language"] = language_filter

            # Search in Qdrant
            results = await self.storage.qdrant.search(
                query_vector=query_vector, top_k=top_k, filters=filters
            )

            # Format results
            formatted_results = [
                {
                    "file_path": r["payload"]["file_path"],
                    "language": r["payload"]["language"],
                    "chunk_type": r["payload"]["chunk_type"],
                    "name": r["payload"].get("name", ""),
                    "lines": f"{r['payload']['start_line']}-{r['payload']['end_line']}",
                    "code": r["payload"]["code"],
                    "relevance_score": round(r["score"], 4),
                }
                for r in results
            ]

            result = {
                "success": True,
                "query": query,
                "results_count": len(formatted_results),
                "results": formatted_results,
            }

            # Cache results
            await self.storage.cache.set(cache_key, result, ttl=1800)  # 30 min

            return result

        except Exception as e:
            logger.error("Semantic search failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def find_symbol(
        self,
        symbol_name: str,
        symbol_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Find symbol definitions and usages."""
        try:
            # Search for symbol in vector store
            query = f"{symbol_type or 'symbol'} {symbol_name}"
            query_vector = await self.embedder.embed(query)

            filters = {}
            if symbol_type:
                filters["chunk_type"] = symbol_type

            results = await self.storage.qdrant.search(
                query_vector=query_vector, top_k=20, filters=filters
            )

            # Filter for exact symbol name matches
            symbol_results = []
            for r in results:
                if r["payload"].get("name") == symbol_name:
                    symbol_results.append(
                        {
                            "file_path": r["payload"]["file_path"],
                            "language": r["payload"]["language"],
                            "type": r["payload"]["chunk_type"],
                            "lines": f"{r['payload']['start_line']}-{r['payload']['end_line']}",
                            "code": r["payload"]["code"],
                        }
                    )

            return {
                "success": True,
                "symbol_name": symbol_name,
                "symbol_type": symbol_type,
                "found_count": len(symbol_results),
                "locations": symbol_results,
            }

        except Exception as e:
            logger.error("Symbol search failed", error=str(e))
            return {"success": False, "error": str(e)}
