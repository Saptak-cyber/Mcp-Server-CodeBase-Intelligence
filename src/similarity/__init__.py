"""Code similarity detection and duplicate finding."""

from .detector import SimilarityDetector
from .ast_diff import ASTDiffer
from .clone_classifier import CloneClassifier

__all__ = ["SimilarityDetector", "ASTDiffer", "CloneClassifier"]
