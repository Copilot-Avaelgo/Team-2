# Bona RAG System - Backend API Documentation

## Overview
The Bona RAG API is a FastAPI-based service that implements the RAG (Retrieval-Augmented Generation) pattern using Azure services:
- **Azure OpenAI** for LLM
- **Azure Cognitive Search** for document retrieval
- **Azure Blob Storage** for document storage

## API Endpoints

### `POST /api/chat`
Process a user query through the RAG pipeline.

**Request:**
```json
{
  "query": "What is the drying time for Bona Classic?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "answer": "Bona Classic has a drying time of 6-8 hours between coats...",
  "source_documents": [
    {
      "content": "Product: Bona Classic\nDrying time: 6-8 hours...",
      "source": "Bona_Classic_TDS_AU.txt",
      "score": 0.95
    }
  ],
  "session_id": "optional-session-id"
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid request (empty query)
- `500`: Server error

### `GET /api/health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "rag_service_ready": true,
  "environment": "production"
}
```

### `GET /`
Root endpoint with links to documentation.

## Configuration

### Environment Variables
Set these in `.env` file or Azure App Service configuration:

```env
# Azure OpenAI
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo

# Azure Cognitive Search
AZURE_SEARCH_SERVICE_NAME=<service-name>
AZURE_SEARCH_API_KEY=<api-key>
AZURE_SEARCH_INDEX_NAME=bona-products

# Azure Blob Storage
AZURE_STORAGE_ACCOUNT_NAME=<account-name>
AZURE_STORAGE_ACCOUNT_KEY=<account-key>
AZURE_STORAGE_CONTAINER_NAME=documents

# Application
ENVIRONMENT=production  # or development
LOG_LEVEL=INFO
```

## Architecture

### Services

#### `RAGService` (`src/services/__init__.py`)
Orchestrates the complete RAG pipeline:
1. Retrieves relevant documents from Cognitive Search
2. Generates LLM response using retrieved context
3. Returns response with source documents

#### `SearchService` (`src/services/search_service.py`)
Manages Azure Cognitive Search interactions:
- `search_documents(query)` - Full-text + semantic search
- `index_documents(documents)` - Upload documents to index

#### `LLMService` (`src/services/llm_service.py`)
Manages Azure OpenAI interactions:
- `generate_response(query, context)` - Generate RAG response
- Implements prompt engineering for product Q&A

#### `DocumentProcessor` (`src/services/document_processor.py`)
Processes TXT documents:
- Splits documents into chunks (500 words, 100-word overlap)
- Generates document metadata

## Running Locally

### Prerequisites
- Python 3.11+
- Azure credentials

### Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Create .env file with your Azure credentials
cp .env.example .env
# Edit .env with real values
```

### Start Development Server
```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at `http://localhost:8000`

### API Documentation
Interactive API docs available at: `http://localhost:8000/docs`

## Deployment

### Docker
```bash
docker build -t bona-rag-api:latest backend/
docker run -p 8000:8000 --env-file backend/.env bona-rag-api:latest
```

### Azure App Service
Deployment via GitHub Actions - see `.github/workflows/deploy.yml`

#### Manual Deployment
```bash
az webapp deployment source config-zip \
  --resource-group bona-rag-rg \
  --name bona-api \
  --src backend/
```

## Testing

### Run Tests
```bash
cd backend
pip install pytest pytest-cov
pytest tests/ -v --cov=src
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Test Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Bona Classic?"}'
```

## Performance & Scaling

### Latency Targets
- Chat response: < 5 seconds
- First token (streaming, if enabled): < 2 seconds

### Bottlenecks
1. **Cognitive Search**: ~500ms for search
2. **Azure OpenAI API**: ~3-4s for generation
3. **Token counting**: Minimal impact

### Optimization Tips
- Use semantic search + BM25 hybrid mode in Cognitive Search
- Implement response caching for common queries
- Use smaller model (gpt-3.5-turbo) for latency
- Implement request batching for high throughput

## Monitoring

### Azure Application Insights (Optional)
```python
from azure.monitor.opentelemetry import configure_azure_monitor
configure_azure_monitor()
```

### Logging
Structured logs to stdout - visible in:
- Azure App Service logs
- Container logs
- Application Insights

## Error Handling

- **Missing credentials**: Returns 503 Service Unavailable
- **No documents retrieved**: Returns 200 with empty sources + fallback message
- **API errors**: Returns 500 with error description

## Rate Limiting

Currently no built-in rate limiting (stateless design). For production:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@router.post("/api/chat")
@limiter.limit("10/minute")
async def chat(request: ChatRequest):
    ...
```

## Troubleshooting

### "Cognitive Search index not found"
- Ensure AZURE_SEARCH_INDEX_NAME exists
- Run document initialization script first

### "No documents retrieved"
- Check Cognitive Search has indexed documents
- Verify query matches indexed content

### "Azure OpenAI quota exceeded"
- Contact Azure support for quota increase
- Implement backoff/retry strategy

## Future Enhancements

- [ ] Document upload endpoint
- [ ] Chat history persistence
- [ ] Multi-turn conversation memory
- [ ] Department-specific context
- [ ] Document feedback mechanism
- [ ] Cost tracking & optimization
