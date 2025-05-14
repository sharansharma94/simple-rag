"""Tests for the vector store module."""
import pytest
from vector_store import QdrantStore
from models import Document

@pytest.mark.asyncio
async def test_vector_store_initialization():
    """Test vector store initialization."""
    store = QdrantStore()
    assert store is not None
    assert store.collection_name == "documents"

@pytest.mark.asyncio
async def test_get_embedding():
    """Test embedding generation."""
    store = QdrantStore()
    text = "Test document"
    embedding = await store.get_embedding(text)
    assert embedding is not None
    assert len(embedding) == 4096  # Mistral embedding size

@pytest.mark.asyncio
async def test_add_and_search_document():
    """Test adding and searching documents."""
    store = QdrantStore()
    doc = Document(
        text="Artificial Intelligence is transforming industries",
        metadata={"source": "test"}
    )
    
    # Add document
    await store.add_document(doc)
    
    # Search
    results = await store.search("What is AI?", k=1)
    assert len(results) > 0
    assert isinstance(results[0], Document)
    assert "Artificial Intelligence" in results[0].text
