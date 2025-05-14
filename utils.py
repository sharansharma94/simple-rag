"""Utility functions for the RAG pipeline."""
import logging
from typing import List
from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def chunk_text(text: str) -> List[str]:
    """Split text into chunks with overlap."""
    settings = get_settings()
    chunk_size = settings.CHUNK_SIZE
    overlap = settings.CHUNK_OVERLAP
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Move start position for next chunk, considering overlap
        start = end - overlap if end < len(text) else len(text)
    
    return chunks

def format_prompt(query: str, context: str) -> str:
    """Format prompt for the LLM."""
    return f"""Answer the question based on the context below. If you cannot find the answer in the context, say "I cannot answer this question based on the provided context."

Context:
{context}

Question:
{query}

Answer:"""
