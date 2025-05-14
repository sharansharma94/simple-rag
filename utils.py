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
        end = start + chunk_size
        # If this is not the first chunk, back up to include overlap
        if start > 0:
            start = start - overlap
        chunk = text[start:end]
        chunks.append(chunk)
        start = end
    
    return chunks

def format_prompt(query: str, context: str) -> str:
    """Format prompt for the LLM."""
    return f"""Answer the question based on the context below. If you cannot find the answer in the context, say "I cannot answer this question based on the provided context."

Context:
{context}

Question:
{query}

Answer:"""
