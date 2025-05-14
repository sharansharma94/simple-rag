# RAG Pipeline with Ollama

A lightweight Retrieval-Augmented Generation (RAG) pipeline using FastAPI and Ollama. This system allows you to upload documents and ask questions about them, using Ollama's embeddings for semantic search and text generation for answers.

## Features

- 🚀 FastAPI-based REST API
- 📑 Document chunking and indexing
- 🔍 Semantic search using Ollama embeddings
- 💡 Question answering using Ollama's Mistral model
- 🔄 Simple in-memory vector store with cosine similarity

## Prerequisites

1. Install [Ollama](https://ollama.ai/)
2. Pull the Mistral model:
   ```bash
   ollama pull mistral
   ```
3. Python 3.12 or higher

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd rag-pipeline
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

1. Start the Ollama server (it should run on port 11434)

2. Start the RAG server:
   ```bash
   python rag_pipeline.py
   ```
   The server will run on `http://localhost:8000`

## API Endpoints

### 1. Upload Document
```http
POST /upload
Content-Type: multipart/form-data

file: <document>
```

Example using curl:
```bash
curl -X POST -F "file=@document.txt" http://localhost:8000/upload
```

### 2. Query Documents
```http
POST /query
Content-Type: application/json

{
    "query": "your question here",
    "num_chunks": 3
}
```

Example using curl:
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"query":"what is this document about?"}' \
     http://localhost:8000/query
```

## How it Works

1. **Document Processing**:
   - Documents are split into chunks with overlap
   - Each chunk is converted to an embedding using Ollama

2. **Query Processing**:
   - Query is converted to an embedding
   - Most similar chunks are retrieved using cosine similarity
   - Retrieved chunks are used as context for Ollama to generate an answer

## Dependencies

- fastapi: Web framework
- uvicorn: ASGI server
- httpx: Async HTTP client
- numpy & scipy: Vector operations
- python-multipart: File upload handling
- pydantic: Data validation

## Contributing

Feel free to open issues or submit pull requests for improvements!

## License

MIT License - feel free to use this code for your projects!
