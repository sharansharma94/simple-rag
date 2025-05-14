"""Tests for the LLM service."""
import pytest
from llm import LLMService

@pytest.mark.asyncio
async def test_llm_generation():
    """Test LLM response generation."""
    service = LLMService()
    query = "What is Python?"
    context = "Python is a high-level programming language."
    
    response = await service.generate(query, context)
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
