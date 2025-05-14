"""LLM service for text generation."""
import httpx
import logging
from typing import Optional
from fastapi import HTTPException

from config import get_settings
from utils import format_prompt

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with the LLM."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.settings = get_settings()
    
    async def generate(self, query: str, context: str) -> str:
        """Generate answer using LLM."""
        try:
            prompt = format_prompt(query, context)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.settings.OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": self.settings.OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                logger.debug(f"LLM response: {result}")
                
                return result["response"]
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating response: {str(e)}"
            )
