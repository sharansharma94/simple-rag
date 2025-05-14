from typing import List, Dict, Optional
from dataclasses import dataclass
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn
import numpy as np
from scipy.spatial.distance import cosine
from collections import defaultdict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@dataclass
class Document:
    text: str
    metadata: Dict
    embedding: Optional[np.ndarray] = None

class SimpleVectorStore:
    def __init__(self):
        self.documents: List[Document] = []
    
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
        doc = Document(text=text, metadata=metadata, embedding=embedding)
        self.documents.append(doc)
    
    async def search(self, query: str, k: int = 3) -> List[Document]:
        query_embedding = await self.get_embedding(query)
        
        if not self.documents:
            return []
        
        # Calculate cosine similarities
        similarities = [
            (1 - cosine(query_embedding, doc.embedding), doc)
            for doc in self.documents
        ]
        
        # Sort by similarity
        similarities.sort(reverse=True)
        
        return [doc for _, doc in similarities[:k]]

# Initialize vector store
vector_store = SimpleVectorStore()

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
    context = "\n\n".join(doc.text for doc in results)
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
