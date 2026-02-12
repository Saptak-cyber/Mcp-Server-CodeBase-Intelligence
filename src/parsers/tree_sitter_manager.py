"""Tree-sitter parser manager for multi-language support."""

from typing import Dict, Any
from tree_sitter import Language, Parser, Query, QueryCursor
from .language_configs import get_language_config
from ..utils.logging import get_logger

logger = get_logger(__name__)


class TreeSitterManager:
    """Manager for tree-sitter parsers."""

    def __init__(self):
        """Initialize tree-sitter manager."""
        self._parsers: Dict[str, Parser] = {}
        self._languages: Dict[str, Language] = {}
        self._initialize_languages()

    def _initialize_languages(self) -> None:
        """Initialize language parsers."""
        try:
            # Note: In production, you would build and load language .so files
            # For now, we'll use a simplified version
            import tree_sitter_python
            import tree_sitter_javascript
            import tree_sitter_java
            import tree_sitter_go

            self._languages["python"] = Language(tree_sitter_python.language())
            self._languages["javascript"] = Language(tree_sitter_javascript.language())
            self._languages["typescript"] = Language(tree_sitter_javascript.language())
            self._languages["java"] = Language(tree_sitter_java.language())
            self._languages["go"] = Language(tree_sitter_go.language())

            for lang_name, language in self._languages.items():
                parser = Parser()
                parser.language = language  # Updated for tree-sitter 0.21+ API
                self._parsers[lang_name] = parser

            logger.info("Tree-sitter languages initialized")
        except Exception as e:
            logger.error("Failed to initialize tree-sitter", error=str(e))
            raise

    async def parse(self, code: str, language: str) -> Any:
        """Parse code with tree-sitter."""
        if language not in self._parsers:
            raise ValueError(f"Unsupported language: {language}")

        parser = self._parsers[language]
        tree = parser.parse(bytes(code, "utf8"))
        return tree

    async def extract_functions(self, tree: Any, language: str) -> list[Dict[str, Any]]:
        """Extract function definitions from AST."""
        config = get_language_config(language)
        language_obj = self._languages[language]

        query = Query(language_obj, config.function_query)
        cursor = QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        functions = []
        # captures is a dict: {capture_name: [nodes]}
        for capture_name, nodes in captures.items():
            for node in nodes:
                functions.append(
                    {
                        "name": self._get_node_text(node),
                        "start_line": node.start_point[0],
                        "end_line": node.end_point[0],
                        "start_byte": node.start_byte,
                        "end_byte": node.end_byte,
                    }
                )

        return functions

    async def extract_classes(self, tree: Any, language: str) -> list[Dict[str, Any]]:
        """Extract class definitions from AST."""
        config = get_language_config(language)
        language_obj = self._languages[language]

        query = Query(language_obj, config.class_query)
        cursor = QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        classes = []
        # captures is a dict: {capture_name: [nodes]}
        for capture_name, nodes in captures.items():
            for node in nodes:
                classes.append(
                    {
                        "name": self._get_node_text(node),
                        "start_line": node.start_point[0],
                        "end_line": node.end_point[0],
                        "start_byte": node.start_byte,
                        "end_byte": node.end_byte,
                    }
                )

        return classes

    async def extract_imports(self, tree: Any, language: str) -> list[str]:
        """Extract import statements from AST."""
        config = get_language_config(language)
        language_obj = self._languages[language]

        query = Query(language_obj, config.import_query)
        cursor = QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        imports = []
        # captures is a dict: {capture_name: [nodes]}
        for capture_name, nodes in captures.items():
            for node in nodes:
                imports.append(self._get_node_text(node))

        return imports

    def _get_node_text(self, node: Any) -> str:
        """Get text content of a node."""
        return node.text.decode("utf8") if node.text else ""
