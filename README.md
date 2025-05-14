# RAG Pipeline with Qdrant Vector Store

This project implements a Retrieval-Augmented Generation (RAG) pipeline using FastAPI, Qdrant vector database, and Ollama's Mistral model. The code is available at [simple-rag](https://github.com/sharansharma94/simple-rag). This system allows you to upload documents and ask questions about them, using Ollama's embeddings for semantic search and text generation for answers.

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
   git clone https://github.com/sharansharma94/simple-rag.git
   cd simple-rag
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start Qdrant using Docker Compose:
   ```bash
   docker-compose up -d
   ```
   
   Or using Podman:
   ```bash
   mkdir -p data/qdrant
   podman run -d --name qdrant \
     -p 6333:6333 -p 6334:6334 \
     -v ./data/qdrant:/qdrant/storage:Z \
     docker.io/qdrant/qdrant:latest
   ```

## Usage

1. Start the RAG server:
   ```bash
   python rag_pipeline.py
   ```

2. Upload a document:
   ```bash
   curl -X POST -F "file=@sample.txt" http://localhost:8000/upload
   ```

3. Query the system:
   ```bash
   curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"query": "What is RAG?"}' \
     http://localhost:8000/query
   ```

## API Endpoints

### Upload Document
- **URL**: `/upload`
- **Method**: `POST`
- **Form Data**: `file` (text file)
- **Response**: JSON with upload status

### Query
- **URL**: `/query`
- **Method**: `POST`
- **Body**: JSON with `query` field
- **Response**: JSON with answer and context

## Architecture

1. Document Processing:
   - Text is chunked into smaller segments
   - Mistral model generates embeddings (4096 dimensions)
   - Embeddings and text are stored in Qdrant

2. Query Processing:
   - Query is converted to embedding
   - Similar documents are retrieved from Qdrant
   - Mistral model generates answer using retrieved context

## Project Structure

```
.
├── data/               # Qdrant storage directory
├── main.py            # FastAPI application and endpoints
├── config.py          # Configuration management
├── models.py          # Data models and validation
├── utils.py           # Common utility functions
├── vector_store.py    # Vector store implementation
├── llm.py             # LLM service for text generation
├── docker-compose.yml # Docker compose for Qdrant
├── requirements.txt   # Python dependencies
├── .env.example       # Example environment variables
├── README.md         # This file
└── .gitignore        # Git ignore rules
```

## Contributing

Feel free to open issues or submit pull requests for improvements!

## License

MIT License - feel free to use this code for your projects!
