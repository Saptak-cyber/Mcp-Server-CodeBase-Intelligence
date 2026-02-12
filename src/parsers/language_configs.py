"""Language configuration for tree-sitter parsers."""

from dataclasses import dataclass
from typing import List


@dataclass
class LanguageConfig:
    """Configuration for a programming language."""

    name: str
    extensions: List[str]
    function_query: str
    class_query: str
    import_query: str


# Tree-sitter query patterns for different languages
LANGUAGE_CONFIGS = {
    "python": LanguageConfig(
        name="python",
        extensions=[".py"],
        function_query="""
        (function_definition
          name: (identifier) @function.name
        ) @function.definition
        """,
        class_query="""
        (class_definition
          name: (identifier) @class.name
        ) @class.definition
        """,
        import_query="""
        (import_statement) @import
        (import_from_statement) @import
        """,
    ),
    "javascript": LanguageConfig(
        name="javascript",
        extensions=[".js", ".jsx"],
        function_query="""
        (function_declaration
          name: (identifier) @function.name
        ) @function.definition
        (arrow_function) @function.definition
        """,
        class_query="""
        (class_declaration
          name: (identifier) @class.name
        ) @class.definition
        """,
        import_query="""
        (import_statement) @import
        """,
    ),
    "typescript": LanguageConfig(
        name="typescript",
        extensions=[".ts", ".tsx"],
        function_query="""
        (function_declaration
          name: (identifier) @function.name
        ) @function.definition
        (method_definition
          name: (property_identifier) @function.name
        ) @function.definition
        """,
        class_query="""
        (class_declaration
          name: (type_identifier) @class.name
        ) @class.definition
        (interface_declaration
          name: (type_identifier) @class.name
        ) @class.definition
        """,
        import_query="""
        (import_statement) @import
        """,
    ),
    "java": LanguageConfig(
        name="java",
        extensions=[".java"],
        function_query="""
        (method_declaration
          name: (identifier) @function.name
        ) @function.definition
        """,
        class_query="""
        (class_declaration
          name: (identifier) @class.name
        ) @class.definition
        """,
        import_query="""
        (import_declaration) @import
        """,
    ),
    "go": LanguageConfig(
        name="go",
        extensions=[".go"],
        function_query="""
        (function_declaration
          name: (identifier) @function.name
        ) @function.definition
        (method_declaration
          name: (field_identifier) @function.name
        ) @function.definition
        """,
        class_query="""
        (type_declaration) @class.definition
        """,
        import_query="""
        (import_declaration) @import
        """,
    ),
}

# Language aliases: when user requests 'typescript', also include 'tsx'
LANGUAGE_ALIASES = {
    "typescript": ["typescript", "tsx"],
}


def get_language_config(language: str) -> LanguageConfig:
    """Get language configuration."""
    # tsx uses the same queries as typescript
    config_key = language if language in LANGUAGE_CONFIGS else "typescript" if language == "tsx" else language
    if config_key not in LANGUAGE_CONFIGS:
        raise ValueError(f"Unsupported language: {language}")
    return LANGUAGE_CONFIGS[config_key]
