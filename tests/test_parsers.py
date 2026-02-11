"""Tests for parsers module."""

import pytest
from src.parsers.tree_sitter_manager import TreeSitterManager
from src.parsers.symbol_extractor import SymbolExtractor


@pytest.fixture
def parser():
    """Create parser instance."""
    return TreeSitterManager()


@pytest.fixture
def symbol_extractor():
    """Create symbol extractor instance."""
    return SymbolExtractor()


@pytest.mark.asyncio
async def test_parse_python_code(parser):
    """Test parsing Python code."""
    code = """
def hello_world():
    print("Hello, World!")
    
class MyClass:
    def method(self):
        pass
"""
    tree = await parser.parse(code, "python")
    assert tree is not None


@pytest.mark.asyncio
async def test_extract_functions(parser):
    """Test extracting functions from Python code."""
    code = """
def function_one():
    pass

def function_two():
    pass
"""
    tree = await parser.parse(code, "python")
    functions = await parser.extract_functions(tree, "python")
    assert len(functions) >= 2


@pytest.mark.asyncio
async def test_extract_classes(parser):
    """Test extracting classes from Python code."""
    code = """
class ClassOne:
    pass

class ClassTwo:
    pass
"""
    tree = await parser.parse(code, "python")
    classes = await parser.extract_classes(tree, "python")
    assert len(classes) >= 2


@pytest.mark.asyncio
async def test_symbol_extraction(symbol_extractor):
    """Test symbol extraction."""
    code = """
import os
import sys

def my_function():
    pass

class MyClass:
    pass
"""
    symbols = await symbol_extractor.extract_symbols(code, "python")
    assert "functions" in symbols
    assert "classes" in symbols
    assert "imports" in symbols
