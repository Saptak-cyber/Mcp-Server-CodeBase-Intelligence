"""Refactoring analyzer."""

from typing import Dict, Any
from ..storage.storage_manager import StorageManager
from ..utils.file_utils import FileUtils
from .suggestions import RefactoringSuggester
from ..utils.logging import get_logger

logger = get_logger(__name__)


class RefactoringAnalyzer:
    """Analyze code for refactoring opportunities."""

    def __init__(self, storage: StorageManager):
        """Initialize refactoring analyzer."""
        self.storage = storage
        self.suggester = RefactoringSuggester()

    async def analyze(self, file_path: str) -> Dict[str, Any]:
        """Analyze file for refactoring opportunities."""
        try:
            # Get metrics from database
            metrics = await self.storage.neon.get_file_metrics(file_path)

            suggestions = []

            # Analyze metrics for refactoring opportunities
            for metric in metrics:
                if metric.get("cyclomatic_complexity", 0) > 10:
                    suggestions.append(
                        {
                            "type": "high_complexity",
                            "entity": metric["entity_name"],
                            "severity": "warning",
                            "message": f"Cyclomatic complexity of {metric['cyclomatic_complexity']} is high. Consider breaking down into smaller functions.",
                        }
                    )

                if metric.get("maintainability_index", 100) < 50:
                    suggestions.append(
                        {
                            "type": "low_maintainability",
                            "entity": metric["entity_name"],
                            "severity": "warning",
                            "message": "Maintainability index is low. Consider refactoring to improve code quality.",
                        }
                    )

            # Get additional suggestions
            additional = await self.suggester.suggest(file_path, metrics)
            suggestions.extend(additional)

            return {
                "success": True,
                "file_path": file_path,
                "suggestions_count": len(suggestions),
                "suggestions": suggestions,
            }

        except Exception as e:
            logger.error("Refactoring analysis failed", error=str(e))
            return {"success": False, "error": str(e)}
