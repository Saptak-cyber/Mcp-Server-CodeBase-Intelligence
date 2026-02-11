"""Analysis tools for code metrics and dependencies."""

from typing import Dict, Any, Optional
from ..storage.storage_manager import StorageManager
from ..analysis.dependency_graph import DependencyGraphAnalyzer
from ..metrics.calculator import MetricsCalculator
from ..similarity.detector import SimilarityDetector
from ..docs.generator import DocumentationGenerator
from ..refactor.analyzer import RefactoringAnalyzer
from ..utils.logging import get_logger

logger = get_logger(__name__)


class AnalysisTools:
    """Tools for code analysis."""

    def __init__(self, storage: StorageManager):
        """Initialize analysis tools."""
        self.storage = storage
        self.dependency_analyzer = DependencyGraphAnalyzer(storage)
        self.metrics_calculator = MetricsCalculator(storage)
        self.similarity_detector = SimilarityDetector(storage)
        self.doc_generator = DocumentationGenerator()
        self.refactor_analyzer = RefactoringAnalyzer(storage)

    async def analyze_dependencies(
        self, path: str, language: str, depth: int = 3
    ) -> Dict[str, Any]:
        """Analyze dependencies and create graph."""
        try:
            return await self.dependency_analyzer.analyze(path, language, depth)
        except Exception as e:
            logger.error("Dependency analysis failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def compute_metrics(self, file_path: str) -> Dict[str, Any]:
        """Compute code metrics."""
        try:
            return await self.metrics_calculator.compute(file_path)
        except Exception as e:
            logger.error("Metrics computation failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def detect_duplicates(
        self, path: str, similarity_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """Detect duplicate code."""
        try:
            return await self.similarity_detector.detect_duplicates(
                path, similarity_threshold
            )
        except Exception as e:
            logger.error("Duplicate detection failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def generate_docs(self, path: str, format: str = "markdown") -> Dict[str, Any]:
        """Generate documentation."""
        try:
            return await self.doc_generator.generate(path, format)
        except Exception as e:
            logger.error("Documentation generation failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def suggest_refactorings(self, file_path: str) -> Dict[str, Any]:
        """Suggest refactorings."""
        try:
            return await self.refactor_analyzer.analyze(file_path)
        except Exception as e:
            logger.error("Refactoring analysis failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def get_call_graph(
        self, function_name: str, max_depth: int = 2
    ) -> Dict[str, Any]:
        """Get call graph for a function."""
        try:
            return await self.dependency_analyzer.get_call_graph(
                function_name, max_depth
            )
        except Exception as e:
            logger.error("Call graph generation failed", error=str(e))
            return {"success": False, "error": str(e)}
