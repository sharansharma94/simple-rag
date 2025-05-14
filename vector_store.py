"""Vector store implementation using Qdrant."""
import httpx
import numpy as np
import uuid
import logging
from typing import List, Dict, Optional
from fastapi import HTTPException

from config import get_settings
from models import Document

logger = logging.getLogger(__name__)

class QdrantStore:
    """Vector store implementation using Qdrant."""
    
    def __init__(self):
        """Initialize Qdrant client and create collection if needed."""
        self.settings = get_settings()
        self.base_url = f"http://{self.settings.QDRANT_HOST}:{self.settings.QDRANT_PORT}"
        self.collection_name = self.settings.QDRANT_COLLECTION
        
        try:
            self._create_collection()
        except Exception as e:
            logger.warning(f"Collection might already exist: {e}")
    
    def _create_collection(self) -> None:
        """Create Qdrant collection with proper configuration."""
        url = f"{self.base_url}/collections/{self.collection_name}"
        payload = {
            "vectors": {
                "size": self.settings.VECTOR_DIMENSION,
                "distance": "Cosine"
            }
        }
        
        try:
            response = httpx.put(url, json=payload)
            response.raise_for_status()
            logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    async def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding from Ollama API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.settings.OLLAMA_BASE_URL}/api/embeddings",
                    json={"model": self.settings.OLLAMA_MODEL, "prompt": text}
                )
                response.raise_for_status()
                embedding = response.json()["embedding"]
                return np.array(embedding)
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating embedding: {str(e)}"
            )
    
    async def add_document(self, document: Document) -> None:
        """Add document to vector store."""
        try:
            if not document.embedding:
                document.embedding = await self.get_embedding(document.text)
            
            url = f"{self.base_url}/collections/{self.collection_name}/points"
            payload = {
                "points": [{
                    "id": str(uuid.uuid4()),
                    "vector": document.embedding.tolist(),
                    "payload": {
                        "text": document.text,
                        "metadata": document.metadata
                    }
                }]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.put(url, json=payload)
                response.raise_for_status()
                logger.info("Successfully added document to vector store")
        
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error inserting document: {str(e)}"
            )
    
    async def search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """Search for similar documents."""
        if k is None:
            k = self.settings.TOP_K_RESULTS
            
        try:
            query_embedding = await self.get_embedding(query)
            
            url = f"{self.base_url}/collections/{self.collection_name}/points/search"
            payload = {
                "vector": query_embedding.tolist(),
                "limit": k,
                "with_payload": True
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                results = response.json()
            
            logger.debug(f"Search results: {results}")
            
            if not results or "result" not in results:
                return []
            
            return [
                Document(
                    text=hit["payload"]["text"],
                    metadata=hit["payload"].get("metadata", {}),
                    embedding=hit.get("vector")
                )
                for hit in results["result"]
            ]
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error searching documents: {str(e)}"
            )
