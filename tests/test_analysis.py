"""Tests for analysis module."""

import pytest
from src.analysis.dependency_graph import DependencyGraphAnalyzer
from unittest.mock import Mock, AsyncMock


@pytest.mark.asyncio
async def test_dependency_analyzer_initialization():
    """Test dependency analyzer initialization."""
    storage_mock = Mock()
    storage_mock.neo4j = Mock()

    analyzer = DependencyGraphAnalyzer(storage_mock)
    assert analyzer is not None


@pytest.mark.asyncio
async def test_call_graph_generation():
    """Test call graph generation."""
    storage_mock = Mock()
    storage_mock.neo4j = Mock()
    storage_mock.neo4j.execute_query = AsyncMock(return_value=[])

    analyzer = DependencyGraphAnalyzer(storage_mock)
    result = await analyzer.get_call_graph("test_function", max_depth=2)

    assert "success" in result
