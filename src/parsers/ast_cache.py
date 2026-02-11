"""AST caching layer using Redis."""

from typing import Optional, Any
import hashlib
from ..storage.upstash_cache import UpstashCache
from ..utils.logging import get_logger

logger = get_logger(__name__)


class ASTCache:
    """Cache for parsed ASTs."""

    def __init__(self, cache: UpstashCache):
        """Initialize AST cache."""
        self.cache = cache

    def _make_key(self, code: str, language: str) -> str:
        """Create cache key from code hash."""
        code_hash = hashlib.sha256(code.encode()).hexdigest()[:16]
        return f"ast:{language}:{code_hash}"

    async def get(self, code: str, language: str) -> Optional[Any]:
        """Get cached AST."""
        key = self._make_key(code, language)
        return await self.cache.get(key)

    async def set(self, code: str, language: str, ast: Any) -> None:
        """Cache AST."""
        key = self._make_key(code, language)
        await self.cache.set(key, ast, ttl=7200)  # 2 hours
