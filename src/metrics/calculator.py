"""Code metrics calculator."""

from typing import Dict, Any
import os
from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit
from radon.raw import analyze
from ..storage.storage_manager import StorageManager
from ..utils.file_utils import FileUtils
from ..utils.logging import get_logger

logger = get_logger(__name__)


class MetricsCalculator:
    """Calculate code quality metrics."""

    def __init__(self, storage: StorageManager):
        """Initialize metrics calculator."""
        self.storage = storage

    async def compute(self, file_path: str) -> Dict[str, Any]:
        """Compute metrics for a file or directory."""
        try:
            if os.path.isfile(file_path):
                return await self._compute_file_metrics(file_path)
            else:
                return await self._compute_directory_metrics(file_path)

        except Exception as e:
            logger.error("Metrics computation failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def _compute_file_metrics(self, file_path: str) -> Dict[str, Any]:
        """Compute metrics for a single file."""
        try:
            # Only compute for Python files with radon
            if not file_path.endswith(".py"):
                return {
                    "success": True,
                    "file_path": file_path,
                    "message": "Metrics only available for Python files",
                }

            # Read file
            content = await FileUtils.read_file(file_path)

            # Cyclomatic complexity
            cc_results = cc_visit(content)
            complexity_scores = [
                {
                    "name": item.name,
                    "type": getattr(item, "classname", getattr(item, "type", "function")),
                    "complexity": item.complexity,
                    "line": item.lineno,
                }
                for item in cc_results
            ]

            # Maintainability index
            mi_score = mi_visit(content, True)

            # Halstead metrics
            halstead = h_visit(content)

            # Raw metrics (SLOC, comments, etc.)
            raw = analyze(content)

            # Store in database
            metrics_data = [
                {
                    "file_path": file_path,
                    "entity_type": "file",
                    "entity_name": os.path.basename(file_path),
                    "cyclomatic_complexity": sum(item.complexity for item in cc_results)
                    / max(len(cc_results), 1),
                    "maintainability_index": mi_score,
                    "sloc": raw.sloc,
                    "comment_lines": raw.comments,
                    "blank_lines": raw.blank,
                }
            ]

            await self.storage.neon.insert_metrics(metrics_data)

            return {
                "success": True,
                "file_path": file_path,
                "metrics": {
                    "maintainability_index": round(mi_score, 2),
                    "average_complexity": round(
                        sum(item.complexity for item in cc_results) / max(len(cc_results), 1),
                        2,
                    ),
                    "total_sloc": raw.sloc,
                    "comment_lines": raw.comments,
                    "blank_lines": raw.blank,
                    "complexity_breakdown": complexity_scores,
                    "halstead": {
                        "volume": round(halstead.total.volume, 2) if halstead.total else 0,
                        "difficulty": round(halstead.total.difficulty, 2) if halstead.total else 0,
                        "effort": round(halstead.total.effort, 2) if halstead.total else 0,
                    },
                },
            }

        except Exception as e:
            logger.error(f"Failed to compute metrics for {file_path}", error=str(e))
            return {"success": False, "error": str(e)}

    async def _compute_directory_metrics(self, directory: str) -> Dict[str, Any]:
        """Compute metrics for all files in directory."""
        total_files = 0
        total_complexity = 0
        total_mi = 0
        high_complexity_files = []

        async for file_path, language in FileUtils.scan_directory(directory, ["python"]):
            try:
                result = await self._compute_file_metrics(file_path)
                if result.get("success"):
                    total_files += 1
                    metrics = result.get("metrics", {})
                    total_complexity += metrics.get("average_complexity", 0)
                    total_mi += metrics.get("maintainability_index", 0)

                    if metrics.get("average_complexity", 0) > 10:
                        high_complexity_files.append(
                            {
                                "file": file_path,
                                "complexity": metrics.get("average_complexity"),
                            }
                        )

            except Exception as e:
                logger.error(f"Error processing {file_path}", error=str(e))

        return {
            "success": True,
            "directory": directory,
            "summary": {
                "total_files": total_files,
                "average_complexity": round(total_complexity / max(total_files, 1), 2),
                "average_maintainability": round(total_mi / max(total_files, 1), 2),
                "high_complexity_files": high_complexity_files[:10],
            },
        }
