"""Main FastAPI application for the RAG pipeline."""
import logging
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from models import QueryRequest, QueryResponse, Document
from vector_store import QdrantStore
from llm import LLMService
from utils import chunk_text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Pipeline",
    description="Retrieval-Augmented Generation API using Qdrant and Ollama",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
settings = get_settings()
vector_store = QdrantStore()
llm_service = LLMService()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document."""
    try:
        content = await file.read()
        text = content.decode()
        
        # Split text into chunks
        chunks = chunk_text(text)
        logger.info(f"Split document into {len(chunks)} chunks")
        
        # Process each chunk
        for chunk in chunks:
            document = Document(
                text=chunk,
                metadata={"filename": file.filename}
            )
            await vector_store.add_document(document)
        
        return {"message": f"Document {file.filename} processed and indexed successfully"}
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the RAG pipeline."""
    try:
        # Retrieve relevant documents
        results = await vector_store.search(request.query, request.top_k)
        
        if not results:
            return QueryResponse(
                answer="I cannot answer this question as no relevant documents were found.",
                context=""
            )
        
        # Combine retrieved documents into context
        context = "\n\n".join(doc.text for doc in results)
        
        # Generate answer using LLM
        answer = await llm_service.generate(request.query, context)
        
        return QueryResponse(answer=answer, context=context)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
