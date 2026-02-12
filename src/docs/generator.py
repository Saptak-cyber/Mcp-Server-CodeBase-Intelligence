"""Documentation generator."""

from typing import Dict, Any
from ..utils.file_utils import FileUtils
from ..parsers.symbol_extractor import SymbolExtractor
from .templates import MarkdownTemplate
from ..utils.logging import get_logger

logger = get_logger(__name__)


class DocumentationGenerator:
    """Generate documentation from code."""

    def __init__(self) -> None:
        """Initialize documentation generator."""
        self.symbol_extractor = SymbolExtractor()
        self.template = MarkdownTemplate()

    async def generate(self, path: str, format: str = "markdown") -> Dict[str, Any]:
        """Generate documentation for code."""
        try:
            # Read file
            language = FileUtils.get_language_from_extension(path)
            if not language:
                return {"success": False, "error": "Unsupported file type"}

            code = await FileUtils.read_file(path)

            # Extract symbols
            symbols = await self.symbol_extractor.extract_symbols(code, language)

            # Generate documentation
            if format == "markdown":
                doc_content = await self.template.render(path, symbols)
            else:
                doc_content = "HTML format not yet implemented"

            return {
                "success": True,
                "path": path,
                "format": format,
                "documentation": doc_content,
            }

        except Exception as e:
            logger.error("Documentation generation failed", error=str(e))
            return {"success": False, "error": str(e)}
