"""Data models for the RAG pipeline."""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    """Request model for querying the RAG pipeline."""
    query: str = Field(..., description="The query text to search for")
    top_k: Optional[int] = Field(3, description="Number of documents to retrieve")

class QueryResponse(BaseModel):
    """Response model for RAG pipeline queries."""
    answer: str = Field(..., description="Generated answer")
    context: str = Field(..., description="Retrieved context used for generation")

class Document(BaseModel):
    """Model representing a document in the vector store."""
    text: str = Field(..., description="Document text")
    metadata: Dict = Field(default_factory=dict, description="Document metadata")
    embedding: Optional[List[float]] = Field(None, description="Document embedding")
