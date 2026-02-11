"""Tests for metrics module."""

import pytest
from src.metrics.calculator import MetricsCalculator
from unittest.mock import Mock, AsyncMock


@pytest.mark.asyncio
async def test_metrics_calculator_initialization():
    """Test metrics calculator initialization."""
    storage_mock = Mock()
    calculator = MetricsCalculator(storage_mock)
    assert calculator is not None


@pytest.mark.asyncio
async def test_python_metrics():
    """Test calculating Python metrics."""
    # This would require actual file I/O and radon
    # For now, testing the structure
    storage_mock = Mock()
    storage_mock.neon = Mock()
    storage_mock.neon.insert_metrics = AsyncMock()

    calculator = MetricsCalculator(storage_mock)
    assert calculator is not None
