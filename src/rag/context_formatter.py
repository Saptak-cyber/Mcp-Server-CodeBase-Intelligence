"""Context formatter for RAG responses."""

from typing import List, Dict, Any
from ..utils.logging import get_logger

logger = get_logger(__name__)


class ContextFormatter:
    """Format retrieved contexts for user consumption."""

    async def format(self, question: str, contexts: List[Dict[str, Any]]) -> str:
        """Format contexts into a readable response."""
        if not contexts:
            return "No relevant code found for your question."

        lines = [
            f"Based on your question: '{question}', here are the most relevant code snippets:",
            "",
        ]

        for i, ctx in enumerate(contexts, 1):
            lines.append(f"### Result {i} (Relevance: {ctx['relevance_score']})")
            lines.append(f"**File**: `{ctx['file_path']}`")
            lines.append(f"**Lines**: {ctx['lines']}")
            lines.append(f"**Type**: {ctx['type']}")
            if ctx["name"]:
                lines.append(f"**Name**: `{ctx['name']}`")
            lines.append("")
            lines.append("```" + ctx["language"])
            lines.append(ctx["code"])
            lines.append("```")
            lines.append("")

        lines.append("---")
        lines.append("You can use these code snippets to understand and answer your question.")

        return "\n".join(lines)
