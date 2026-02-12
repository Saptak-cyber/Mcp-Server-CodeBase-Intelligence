"""Symbol extraction from AST."""

from typing import List, Dict, Any
from .tree_sitter_manager import TreeSitterManager
from ..utils.logging import get_logger

logger = get_logger(__name__)


class SymbolExtractor:
    """Extract symbols from code using AST."""

    def __init__(self) -> None:
        """Initialize symbol extractor."""
        self.parser = TreeSitterManager()

    async def extract_symbols(self, code: str, language: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract all symbols from code."""
        try:
            tree = await self.parser.parse(code, language)

            functions = await self.parser.extract_functions(tree, language)
            classes = await self.parser.extract_classes(tree, language)
            imports = await self.parser.extract_imports(tree, language)

            return {
                "functions": functions,
                "classes": classes,
                "imports": imports,  # type: ignore[dict-item]
            }
        except Exception as e:
            logger.error("Symbol extraction failed", error=str(e))
            return {"functions": [], "classes": [], "imports": []}
