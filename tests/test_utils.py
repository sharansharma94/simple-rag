"""Tests for utility functions."""
from utils import chunk_text, format_prompt

def test_chunk_text():
    """Test text chunking."""
    text = "a" * 2000  # Text longer than chunk size
    chunks = chunk_text(text)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 1000  # Default chunk size

def test_format_prompt():
    """Test prompt formatting."""
    query = "What is AI?"
    context = "AI is artificial intelligence."
    prompt = format_prompt(query, context)
    
    assert query in prompt
    assert context in prompt
    assert "Answer:" in prompt
