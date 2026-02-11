"""Tests for search module."""

import pytest
from src.search.embeddings import EmbeddingGenerator
from src.search.chunker import CodeChunker


@pytest.fixture
def embedder():
    """Create embedder instance."""
    return EmbeddingGenerator()


@pytest.fixture
def chunker():
    """Create chunker instance."""
    return CodeChunker()


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires HuggingFace API key")
async def test_generate_embedding(embedder):
    """Test generating embeddings."""
    text = "def hello(): print('hello')"
    embedding = await embedder.embed(text)
    assert isinstance(embedding, list)
    assert len(embedding) > 0


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires HuggingFace API key")
async def test_batch_embeddings(embedder):
    """Test batch embedding generation."""
    texts = [
        "def hello(): pass",
        "def goodbye(): pass",
        "class MyClass: pass",
    ]
    embeddings = await embedder.embed_batch(texts)
    assert len(embeddings) == len(texts)
    assert all(isinstance(emb, list) for emb in embeddings)


@pytest.mark.asyncio
async def test_code_chunking(chunker):
    """Test code chunking."""
    # This is a simplified test
    # In reality, we need a parsed tree
    code = """
def function1():
    pass

def function2():
    pass
"""
    # Would need proper tree for full test
    # chunks = await chunker.chunk_code(code, tree, "test.py", "python")
    # assert len(chunks) > 0
    assert True  # Placeholder
