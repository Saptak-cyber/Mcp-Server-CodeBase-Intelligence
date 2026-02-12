"""Tree-sitter parser manager for multi-language support."""

from typing import Dict, Any, List, Tuple
from tree_sitter import Language, Parser, Query, QueryCursor
from .language_configs import get_language_config
from ..utils.logging import get_logger

logger = get_logger(__name__)


class TreeSitterManager:
    """Manager for tree-sitter parsers."""

    def __init__(self) -> None:
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
            import tree_sitter_typescript
            import tree_sitter_java
            import tree_sitter_go

            self._languages["python"] = Language(tree_sitter_python.language())
            self._languages["javascript"] = Language(tree_sitter_javascript.language())
            self._languages["typescript"] = Language(tree_sitter_typescript.language_typescript())
            self._languages["tsx"] = Language(tree_sitter_typescript.language_tsx())
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

    async def extract_function_calls(
        self, tree: Any, language: str, file_path: str = ""
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Extract function definitions and the calls they make.

        Returns:
            Tuple of (functions, call_pairs) where:
            - functions: list of {name, file_path, start_line, end_line}
            - call_pairs: list of {caller, callee, file_path, line}
        """
        config = get_language_config(language)
        language_obj = self._languages[language]

        # 1. Find all function definitions with their full nodes
        func_query = Query(language_obj, config.function_query)
        func_cursor = QueryCursor(func_query)
        func_captures = func_cursor.captures(tree.root_node)

        functions = []
        func_nodes = []  # (name, body_node) pairs

        # Collect function definitions
        definition_nodes = func_captures.get("function.definition", [])
        name_nodes = func_captures.get("function.name", [])

        for name_node in name_nodes:
            func_name = self._get_node_text(name_node)
            functions.append({
                "name": func_name,
                "file_path": file_path,
                "start_line": name_node.start_point[0] + 1,
                "end_line": name_node.parent.end_point[0] + 1 if name_node.parent else name_node.end_point[0] + 1,
            })

        # Build (func_name, parent_node) pairs for call extraction
        for name_node in name_nodes:
            func_name = self._get_node_text(name_node)
            # The parent of the name is the function_definition node
            func_def_node = name_node.parent
            if func_def_node:
                func_nodes.append((func_name, func_def_node))

        # 2. For each function, find calls within its body
        call_pairs = []

        if not config.call_query:
            return functions, call_pairs

        call_query = Query(language_obj, config.call_query)

        for caller_name, func_def_node in func_nodes:
            # Find the body node within the function definition
            body_node = None
            for child in func_def_node.children:
                if child.type in ("block", "statement_block", "function_body", "method_body"):
                    body_node = child
                    break

            if not body_node:
                # Use the entire function node if no distinct body found
                body_node = func_def_node

            # Run call query on the function body
            call_cursor = QueryCursor(call_query)
            call_captures = call_cursor.captures(body_node)

            seen_callees = set()
            for capture_name, nodes in call_captures.items():
                if capture_name == "call.name":
                    for call_node in nodes:
                        callee_name = self._get_node_text(call_node)
                        # Skip self-recursion and duplicates
                        if callee_name and callee_name != caller_name and callee_name not in seen_callees:
                            seen_callees.add(callee_name)
                            call_pairs.append({
                                "caller": caller_name,
                                "callee": callee_name,
                                "file_path": file_path,
                                "line": call_node.start_point[0] + 1,
                            })

        return functions, call_pairs
