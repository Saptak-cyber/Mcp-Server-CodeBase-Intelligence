"""Documentation templates."""

from typing import Dict, Any, List
from ..utils.logging import get_logger

logger = get_logger(__name__)


class MarkdownTemplate:
    """Markdown documentation template."""

    async def render(self, file_path: str, symbols: Dict[str, List[Dict[str, Any]]]) -> str:
        """Render documentation in Markdown."""
        lines = [
            f"# Documentation for {file_path}",
            "",
            "## Overview",
            "",
            f"This file contains {len(symbols['functions'])} functions and {len(symbols['classes'])} classes.",
            "",
        ]

        # Document classes
        if symbols["classes"]:
            lines.append("## Classes")
            lines.append("")
            for cls in symbols["classes"]:
                lines.append(f"### {cls['name']}")
                lines.append("")
                lines.append(f"Defined at lines {cls['start_line']}-{cls['end_line']}")
                lines.append("")

        # Document functions
        if symbols["functions"]:
            lines.append("## Functions")
            lines.append("")
            for func in symbols["functions"]:
                lines.append(f"### {func['name']}")
                lines.append("")
                lines.append(f"Defined at lines {func['start_line']}-{func['end_line']}")
                lines.append("")

        # Document imports
        if symbols["imports"]:
            lines.append("## Dependencies")
            lines.append("")
            for imp in symbols["imports"][:10]:  # Limit to first 10
                lines.append(f"- `{imp}`")
            lines.append("")

        return "\n".join(lines)
