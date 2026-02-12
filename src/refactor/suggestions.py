"""Refactoring suggestions."""

from typing import List, Dict, Any
from ..utils.logging import get_logger

logger = get_logger(__name__)


class RefactoringSuggester:
    """Generate refactoring suggestions."""

    async def suggest(self, file_path: str, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate refactoring suggestions based on metrics."""
        suggestions = []

        # Check for long functions
        for metric in metrics:
            sloc = metric.get("sloc", 0)
            if sloc > 50:
                suggestions.append(
                    {
                        "type": "long_function",
                        "entity": metric["entity_name"],
                        "severity": "info",
                        "message": f"Function has {sloc} lines. Consider extracting smaller functions.",
                    }
                )

        return suggestions
