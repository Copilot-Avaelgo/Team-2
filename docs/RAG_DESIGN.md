# Bona RAG System - RAG Design Document

## Overview
This document describes the RAG (Retrieval-Augmented Generation) implementation for the Bona product support assistant.

## Architecture Diagram

```
User Input (Chat)
    ↓
[React Frontend]
    ↓
[FastAPI Backend - RAG Orchestrator]
    ├─→ [Document Processor] (batch, on startup)
    │   └─→ TXT Files → Chunks → Embeddings
    │       └─→ [Azure Blob Storage]
    │
    ├─→ [Search Service] (query time)
    │   └─→ [Azure Cognitive Search]
    │       └─→ Top-K Similar Documents
    │
    ├─→ [LLM Service] (query time)
    │   └─→ [Azure OpenAI]
    │       └─→ Augmented Response
    │
    └─→ Response with Sources
    ↓
[React Frontend - Display]
```

## Component Details

### 1. Document Processor
**Purpose**: Prepare product documentation for retrieval

**Input**: TXT files from `ragf/` folder
**Output**: Indexed documents in Cognitive Search

#### Chunking Strategy
- **Chunk Size**: 500 words
- **Overlap**: 100 words (prevents losing context at boundaries)
- **Example**:
  ```
  Document: [Word1, Word2, ..., Word500, Word501, ..., Word1000]
                    ↓
  Chunk1: [Word1...Word500]
  Chunk2: [Word401...Word900]     ← 100-word overlap
  Chunk3: [Word801...Word1300]
  ```

#### Chunk Metadata
```python
{
  "id": "Bona_Classic_TDS_AU.txt_0",
  "content": "Product: Bona Classic... [500 words]",
  "source": "Bona_Classic_TDS_AU.txt"
}
```

### 2. Search Service
**Purpose**: Retrieve relevant documents for a user query

**Service**: Azure Cognitive Search (Free tier)

#### Search Process
1. User query: "What is drying time for Classic?"
2. Cognitive Search performs:
   - **Full-text search**: "drying" + "Classic" matching
   - **Ranking**: BM25 score + relevance
3. Returns: Top 5 documents with scores

#### Example Search Query
```python
results = search_client.search(
  search_text="What is drying time for Classic?",
  top=5,
  select=["content", "source"]
)
```

#### Search Results
```json
[
  {
    "id": "Bona_Classic_TDS_AU.txt_2",
    "content": "Drying time: 6-8 hours between coats...",
    "source": "Bona_Classic_TDS_AU.txt",
    "@search.score": 0.95
  },
  {
    "id": "Bona_Classic_UX_TDS_AU.txt_1",
    "content": "Ultra-fast drying option...",
    "source": "Bona_Classic_UX_TDS_AU.txt",
    "@search.score": 0.82
  }
]
```

### 3. LLM Service
**Purpose**: Generate accurate response augmented with retrieved context

**Service**: Azure OpenAI (gpt-3.5-turbo)

#### RAG Prompt Pattern
```
SYSTEM:
"You are a helpful assistant for Bona flooring products. 
Answer questions based on the provided product documentation. 
If you don't know the answer, say so."

USER:
"Based on the following Bona product documentation, answer the user's question:

DOCUMENTATION:
[Retrieved Documents - top 5, concatenated]

USER QUESTION:
What is drying time for Bona Classic?

ANSWER:"
```

#### Response Generation
1. Combine system prompt + user query + context
2. Call Azure OpenAI API
3. Stream or return full response
4. Temperature: 0.7 (balanced creativity/accuracy)
5. Max tokens: 512

#### Example Response
```
Bona Classic has a drying time of 6-8 hours between coats, 
making it suitable for high-traffic residential areas. 
For faster results, consider Bona Classic UX which dries in 3-4 hours.
```

### 4. RAG Orchestrator
**Purpose**: Coordinate entire retrieval + generation pipeline

#### Process Flow
```
1. Receive query from user
   ↓
2. Call SearchService.search_documents(query)
   → Retrieve 5 most relevant document chunks
   ↓
3. If no documents found:
   → Return fallback message (no re-querying)
   ↓
4. Call LLMService.generate_response(query, documents)
   → Build RAG prompt
   → Call Azure OpenAI
   → Get response
   ↓
5. Return ChatResponse with:
   - answer (from LLM)
   - source_documents (retrieved chunks with scores)
   - session_id (for tracking)
```

## Data Flow Example

**User Query**: "How long does Bona TrafficHD take to dry?"

### Step 1: Search
```python
query = "How long does Bona TrafficHD take to dry?"
retrieved_docs = search_service.search_documents(query, top_k=5)

# Returns:
[
  {
    "content": "Bona TrafficHD Ultra: 4-hour dry time...",
    "source": "Bona_TrafficHD_TDS_AU.txt",
    "score": 0.98
  },
  {
    "content": "Bona Traffic HD Raw AU: water-based...",
    "source": "Bona_Traffic_HD_Raw_AU_TDS.txt",
    "score": 0.91
  },
  # ... 3 more results
]
```

### Step 2: Generate Response
```python
prompt = """
Based on the following Bona product documentation, answer the user's question:

DOCUMENTATION:
Source: Bona_TrafficHD_TDS_AU.txt
Bona TrafficHD Ultra: 4-hour dry time between coats, 
water-based, eco-friendly finish...

Source: Bona_Traffic_HD_Raw_AU_TDS.txt
Bona Traffic HD Raw AU: water-based polyurethane...
---

USER QUESTION:
How long does Bona TrafficHD take to dry?

ANSWER:
"""

response = llm_service.generate_response(prompt)

# Returns:
"Bona TrafficHD Ultra has a 4-hour dry time between coats, 
making it ideal for projects with faster turnaround times. 
It's a water-based finish that's environmentally friendly. 
For more information on other TrafficHD variants, refer to 
the product documentation."
```

### Step 3: Return to User
```json
{
  "answer": "Bona TrafficHD Ultra has a 4-hour dry time...",
  "source_documents": [
    {
      "content": "Bona TrafficHD Ultra: 4-hour dry time...",
      "source": "Bona_TrafficHD_TDS_AU.txt",
      "score": 0.98
    },
    # ... more sources
  ],
  "session_id": "session-1234567890"
}
```

## Performance Considerations

### Latency Breakdown (typical)
- Search: 300-500ms
- LLM Generation: 2-4 seconds
- Network: 200-500ms
- **Total**: 2.5-5 seconds

### Optimization Strategies
1. **Caching**
   - Cache frequent queries
   - Cache embeddings
   - TTL: 1 hour

2. **Batching**
   - Group related queries
   - Batch to Azure OpenAI

3. **Chunking**
   - Smaller chunks = faster retrieval
   - Trade-off: lose context

4. **Indexing**
   - Add semantic search to Cognitive Search
   - Use BM25 + semantic hybrid mode

## Limitations & Known Issues

### MVP Limitations
1. **No chat history**: Each query is independent
   - Workaround: Include context in query
   
2. **No authentication**: Public endpoint
   - Workaround: Rate limit by IP
   
3. **Static documents**: No real-time upload
   - Workaround: Pre-index all docs at startup
   
4. **Free tier limits**: 50 MB, 10k docs/day
   - Upgrade to Standard if needed

### Document Quality Issues
1. **Poor quality source**: Garbage in → Garbage out
   - Mitigation: Human review of TDS sheets
   
2. **Missing information**: Not in docs → Model won't answer
   - Mitigation: Add to TDS sheets
   
3. **Outdated info**: Docs not kept current
   - Mitigation: Quarterly doc reviews

## Future Enhancements

### Phase 2: Advanced RAG
- [ ] Semantic search with embeddings
- [ ] Multi-turn conversation memory
- [ ] Document feedback loop (rating responses)
- [ ] A/B testing different prompts

### Phase 3: Scaling
- [ ] Chat history in Cosmos DB
- [ ] User authentication & profiles
- [ ] Department-specific contexts
- [ ] Real-time document upload

### Phase 4: Intelligence
- [ ] Feedback-driven prompt optimization
- [ ] Cost tracking per query
- [ ] Custom fine-tuning on Bona docs
- [ ] Multilingual support

## Testing RAG Quality

### Manual Testing
```bash
# Test queries
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the drying time for Bona Classic?"}'

curl -X POST http://localhost:8000/api/chat \
  -d '{"query": "How do I apply Bona Wave2K?"}'

curl -X POST http://localhost:8000/api/chat \
  -d '{"query": "What is the VOC content of Bona products?"}'
```

### Evaluation Metrics
1. **Relevance**: Retrieved docs match query intent
2. **Accuracy**: LLM answer is factually correct
3. **Completeness**: Answer addresses full query
4. **Latency**: Response within 5 seconds

### Test Dataset
Create a test set of 20-30 questions with expected answers, test against:
- Before/after optimizations
- Different prompts
- Different LLM models

## Monitoring & Debugging

### Key Metrics
```python
{
  "query": str,
  "num_docs_retrieved": int,
  "search_latency_ms": float,
  "llm_latency_ms": float,
  "total_latency_ms": float,
  "tokens_used": int,
  "cost": float,
  "user_rating": Optional[int]  # 1-5 stars
}
```

### Logging
All events logged to stdout in JSON format:
```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "level": "INFO",
  "service": "rag_service",
  "query": "drying time",
  "docs_retrieved": 5,
  "latency_ms": 3200,
  "session_id": "session-123"
}
```

## Cost Analysis

### Per-Query Costs (typical)
- Cognitive Search: ~$0.0001 (free tier included)
- Azure OpenAI gpt-3.5-turbo:
  - Input: ~150 tokens × $0.0005/1k = $0.000075
  - Output: ~100 tokens × $0.0015/1k = $0.00015
  - **Per query**: ~$0.00025

### Monthly Costs (100 users, 500 queries)
- 500 queries × $0.00025 = $0.125
- App Service: $12
- Storage: $1
- **Total**: ~$13/month (well under budget)

## References
- Azure OpenAI: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/
- Cognitive Search: https://learn.microsoft.com/en-us/azure/search/
- RAG Pattern: https://python.langchain.com/docs/use_cases/question_answering/
