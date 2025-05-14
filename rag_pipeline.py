from typing import List, Dict, Optional
from dataclasses import dataclass
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn
import numpy as np
import json
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QdrantStore:
    def __init__(self):
        self.base_url = "http://localhost:6333"
        self.collection_name = "documents"
        self.dim = 4096  # Mistral embedding dimension
        
        # Create collection if it doesn't exist
        try:
            self._create_collection()
        except Exception as e:
            print(f"Collection might already exist: {e}")
    
    def _create_collection(self):
        url = f"{self.base_url}/collections/{self.collection_name}"
        payload = {
            "vectors": {
                "size": self.dim,
                "distance": "Cosine"
            }
        }
        response = httpx.put(url, json=payload)
        response.raise_for_status()
    
    async def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding from Ollama API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/embeddings",
                json={
                    "model": "mistral",
                    "prompt": text
                }
            )
            result = response.json()
            return np.array(result["embedding"])
    
    async def add_document(self, text: str, metadata: Dict):
        embedding = await self.get_embedding(text)
        point_id = str(uuid.uuid4())
        
        try:
            url = f"{self.base_url}/collections/{self.collection_name}/points"
            payload = {
                "points": [{
                    "id": point_id,
                    "vector": embedding.tolist(),
                    "payload": {
                        "text": text,
                        "metadata": metadata
                    }
                }]
            }
            response = httpx.put(url, json=payload)
            response.raise_for_status()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error inserting document: {str(e)}")
    

    async def search(self, query: str, k: int = 3) -> List[Dict]:
        query_embedding = await self.get_embedding(query)
        
        try:
            url = f"{self.base_url}/collections/{self.collection_name}/points/search"
            payload = {
                "vector": query_embedding.tolist(),
                "limit": k,
                "with_payload": True
            }
            
            # Validate payload
            if not isinstance(payload, dict):
                raise ValueError("Invalid payload structure")
            
            # Log payload for debugging
            print("Search payload:", payload)
            
            response = httpx.post(url, json=payload)
            response.raise_for_status()
            results = response.json()
            
            # Log results for debugging
            print("Search results:", results)
            
            if not results or "result" not in results:
                return []
                
            return [{
                "text": hit.get("payload", {}).get("text", ""),
                "metadata": hit.get("payload", {}).get("metadata", {}),
                "score": hit.get("score", 0.0)
            } for hit in results["result"]]
        except httpx.HTTPError as e:
            print(f"HTTP error: {e}")
            raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")
# Initialize vector store
vector_store = QdrantStore()

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Simple text chunking"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and index a document."""
    content = await file.read()
    text = content.decode("utf-8")
    
    # Split text into chunks
    chunks = chunk_text(text)
    
    # Add chunks to vector store
    for i, chunk in enumerate(chunks):
        await vector_store.add_document(
            text=chunk,
            metadata={"source": file.filename, "chunk_id": i}
        )
    
    return {"message": f"Document {file.filename} processed and indexed successfully"}

from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    num_chunks: int = 3


@app.post("/query")
async def query(request: QueryRequest):
    print(f"Received query: {request.query}")
    
    # Retrieve relevant chunks
    results = await vector_store.search(request.query, k=request.num_chunks)
    # print(f"Retrieved {len(results)} chunks")
    
    # Combine retrieved chunks into context
    context = "\n\n".join(doc["text"] for doc in results)
    # print(f"Context: {context}")
    
    # Prepare prompt for Ollama
    prompt = f"""Use the following context to answer the question. If you cannot answer based on the context, say so.

Context:
{context}

Question: {request.query}

Answer:"""
    print(f"Prompt: {prompt}")
    
    # Query Ollama
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            }
        )
        result = response.json()
        print(f"Ollama response: {result}")
    
    return {
        "answer": result["response"],
        "context": context
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
