"""Input validation utilities."""

import os
from typing import List
from pydantic import BaseModel, field_validator


class PathValidator(BaseModel):
    """Validate file paths."""

    path: str

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate that path exists and is accessible."""
        if not v:
            raise ValueError("Path cannot be empty")

        # Normalize path
        normalized = os.path.normpath(os.path.abspath(v))

        # Check for directory traversal
        if ".." in v:
            raise ValueError("Directory traversal not allowed")

        # Check if path exists
        if not os.path.exists(normalized):
            raise ValueError(f"Path does not exist: {normalized}")

        return normalized


class LanguageValidator(BaseModel):
    """Validate programming language."""

    language: str

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language is supported."""
        supported = ["python", "javascript", "typescript", "java", "go"]
        if v.lower() not in supported:
            raise ValueError(f"Unsupported language: {v}. Supported: {', '.join(supported)}")
        return v.lower()


def validate_path(path: str) -> str:
    """Validate and normalize a file path."""
    validator = PathValidator(path=path)
    return validator.path


def validate_language(language: str) -> str:
    """Validate a programming language."""
    validator = LanguageValidator(language=language)
    return validator.language


def validate_languages(languages: List[str]) -> List[str]:
    """Validate a list of programming languages."""
    return [validate_language(lang) for lang in languages]
