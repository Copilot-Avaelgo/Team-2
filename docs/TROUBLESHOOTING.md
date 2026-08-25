# Troubleshooting Guide

## Common Issues & Solutions

### Backend Issues

#### 1. "Module not found: pydantic_settings"
**Error**: `ModuleNotFoundError: No module named 'pydantic_settings'`

**Solution**:
```bash
cd backend
pip install --upgrade pydantic pydantic-settings
```

#### 2. "Azure credentials not found"
**Error**: `CredentialUnavailableError: No credentials found`

**Solution**:
1. Create `.env` file in `backend/` folder
2. Copy from `.env.example`
3. Fill in real Azure credentials
4. Verify file exists and is readable

#### 3. "Cognitive Search index not found"
**Error**: `ResourceNotFoundError: The resource was not found`

**Solution**:
1. Ensure index exists in Azure Cognitive Search
2. Check `AZURE_SEARCH_INDEX_NAME` matches Azure
3. Run document indexing:
```python
from src.services import RAGService
rag = RAGService()
rag.initialize_knowledge_base('../ragf')
```

#### 4. "No documents retrieved"
**Error**: Empty source_documents in response

**Cause**: Cognitive Search index empty or query doesn't match docs

**Solution**:
1. Verify TXT files in `ragf/` folder
2. Check documents were indexed:
```bash
curl -X GET "https://<service>.search.windows.net/indexes/bona-products/docs/count?api-version=2023-11-01" \
  -H "api-key: <api-key>"
```
3. Test search directly:
```bash
curl -X POST "https://<service>.search.windows.net/indexes/bona-products/docs/search?api-version=2023-11-01" \
  -H "api-key: <api-key>" \
  -H "Content-Type: application/json" \
  -d '{"search": "Bona Classic"}'
```

#### 5. "Azure OpenAI quota exceeded"
**Error**: `RateLimitError: Rate limit exceeded` or `QuotaError`

**Solution**:
1. Wait 1 minute and retry (short quota limits)
2. Request quota increase in Azure Portal
3. Implement exponential backoff:
```python
import time
max_retries = 3
for attempt in range(max_retries):
    try:
        response = llm_service.generate_response(...)
        break
    except RateLimitError:
        wait_time = 2 ** attempt
        time.sleep(wait_time)
```

#### 6. "FastAPI app won't start"
**Error**: `ERROR: Application startup failed`

**Solution**:
1. Check Python version: `python --version` (must be 3.9+)
2. Verify all dependencies installed:
```bash
pip install -r requirements.txt -v
```
3. Check for import errors:
```bash
python -c "from src.main import app"
```
4. Check Azure credentials format
5. Look for typos in `.env` file

#### 7. "Port 8000 already in use"
**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# Or use different port
uvicorn src.main:app --port 8001
```

---

### Frontend Issues

#### 1. "npm: command not found"
**Error**: `command not found: npm`

**Solution**:
1. Install Node.js 18+: https://nodejs.org/
2. Verify installation: `node --version && npm --version`
3. Restart terminal

#### 2. "Cannot find module '@vitejs/plugin-react'"
**Error**: `Cannot find module '@vitejs/plugin-react'`

**Solution**:
```bash
cd frontend
npm install
```

#### 3. "Frontend can't connect to backend"
**Error**: 500 error or "Network Error" in chat

**Cause**: Backend not running or CORS misconfigured

**Solution**:
1. Verify backend is running:
```bash
curl http://localhost:8000/api/health
```

2. Check Vite proxy config in `vite.config.ts`:
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

3. For production, check backend CORS:
```python
# In backend src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specific domain
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 4. "Build fails"
**Error**: `Failed to compile` or `build error`

**Solution**:
1. Clear node_modules:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

2. Type check:
```bash
npm run type-check
```

3. Look for TypeScript errors:
```bash
npx tsc --noEmit
```

#### 5. "Port 3000 already in use"
**Error**: `error listen EADDRINUSE: address already in use :::3000`

**Solution**:
```bash
# Kill process on port 3000
lsof -i :3000 | grep -v PID | awk '{print $2}' | xargs kill -9  # Linux/Mac
netstat -ano | findstr :3000 | taskkill /PID <PID> /F  # Windows

# Or use different port
npm run dev -- --port 3001
```

#### 6. "API key not working"
**Error**: 401 Unauthorized or authentication failure

**Solution**:
1. Check environment variable in browser console:
```javascript
console.log(import.meta.env.VITE_API_BASE)
```

2. Verify API URL in requests:
```javascript
// In src/services/api.ts
const API_BASE = import.meta.env.VITE_API_BASE || '/api'
console.log('API Base:', API_BASE)
```

3. For development with backend on different port:
```bash
# In vite.config.ts proxy
target: 'http://localhost:8000'
```

---

### Deployment Issues

#### 1. "GitHub Actions workflow fails"
**Error**: Red X in Actions tab

**Solution**:
1. Click on failed workflow
2. Expand failed step
3. Read error message
4. Common causes:
   - Missing GitHub Secrets
   - Wrong Azure credentials
   - Python/Node version mismatch

#### 2. "Azure deployment times out"
**Error**: `Deployment failed - timeout`

**Solution**:
1. Check if App Service started:
```bash
az webapp show --resource-group bona-rag-rg --name bona-api --query state
```

2. Check deployment logs:
```bash
az webapp log tail --resource-group bona-rag-rg --name bona-api
```

3. Increase timeout in `.github/workflows/deploy.yml`

#### 3. "Static Web Apps deployment fails"
**Error**: Frontend deploy fails in Actions

**Solution**:
1. Verify deployment token is correct (starts with "?")
2. Check `staticwebapp.config.json` is valid JSON
3. Verify build output is in `dist/` folder
4. Check logs in Azure Static Web Apps portal

#### 4. "Environment variables not set"
**Error**: API returns 503 (RAG service not ready)

**Solution**:
1. Go to App Service → Configuration → Application settings
2. Add all environment variables from `.env.example`
3. Save settings
4. Restart App Service

#### 5. "Docker build fails"
**Error**: Docker build error locally

**Solution**:
```bash
# Rebuild without cache
docker build --no-cache -t bona-rag-api:latest backend/

# Check Dockerfile syntax
docker run --rm -i hadolint/hadolint < backend/Dockerfile

# Test locally
docker run -p 8000:8000 --env-file backend/.env bona-rag-api:latest
```

---

### Azure Resource Issues

#### 1. "Free tier limits exceeded"
**Error**: "Quota exceeded" or "Service unavailable"

**Limits**:
- Cognitive Search Free: 50 MB, 10k docs/day
- Static Web Apps Free: Limited bandwidth
- App Service B1: 1 vCPU, 1.75 GB RAM

**Solution**: Upgrade to paid tier (see docs/DEPLOYMENT.md)

#### 2. "High Azure bills"
**Cause**: Unoptimized queries or Azure OpenAI usage

**Solution**:
1. Monitor spend:
```bash
az cost management query create --definition '{...}'
```

2. Optimize token usage:
   - Smaller chunks
   - Fewer documents retrieved (top 3 instead of 5)
   - Use gpt-3.5-turbo instead of gpt-4

3. Implement caching:
```python
from functools import lru_cache
@lru_cache(maxsize=100)
def search_documents_cached(query):
    return search_service.search_documents(query)
```

#### 3. "Cognitive Search index corrupted"
**Error**: Searches return no results or wrong results

**Solution**:
1. Delete index:
```bash
az search index delete \
  --resource-group bona-rag-rg \
  --service-name bona-search \
  --index-name bona-products
```

2. Re-index documents:
```python
from src.services import RAGService
rag = RAGService()
rag.initialize_knowledge_base('../ragf')
```

---

### Performance Issues

#### 1. "Responses are slow (>5 sec)"
**Cause**: Azure OpenAI latency or Cognitive Search delay

**Solution**:
1. Enable query caching (common questions)
2. Reduce retrieved documents: `top_k=3` instead of 5
3. Use gpt-3.5-turbo (faster than gpt-4)
4. Check Azure OpenAI region (use same region as app)

#### 2. "High latency on first request"
**Cause**: Cold start of App Service

**Solution**:
1. App Service hibernates after 20 mins idle
2. Add warm-up via GitHub Actions:
```bash
# Add to .github/workflows/deploy.yml
- name: Warm up API
  run: curl -f https://bona-api.azurewebsites.net/api/health
```

#### 3. "Memory usage growing"
**Cause**: Memory leak in FastAPI or Cognitive Search client

**Solution**:
1. Restart App Service:
```bash
az webapp restart --resource-group bona-rag-rg --name bona-api
```

2. Check for leaks:
```python
import tracemalloc
tracemalloc.start()
# ... run queries ...
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1e6}; Peak: {peak / 1e6}")
```

---

## Debug Checklist

Before reporting an issue:

- [ ] Read error message carefully
- [ ] Check logs:
  ```bash
  # Backend
  docker logs <container-id>
  az webapp log tail --resource-group bona-rag-rg --name bona-api
  
  # Frontend browser console
  F12 → Console tab → check for errors
  ```

- [ ] Verify credentials:
  ```bash
  echo $AZURE_OPENAI_API_KEY  # Linux/Mac
  echo %AZURE_OPENAI_API_KEY%  # Windows
  ```

- [ ] Test components independently:
  ```bash
  # Test backend API
  curl http://localhost:8000/api/health
  
  # Test frontend build
  cd frontend && npm run build
  ```

- [ ] Check Azure Portal for resource health
- [ ] Verify all GitHub Secrets are set

## Getting Help

1. **Check Documentation**:
   - docs/API.md - API reference
   - docs/DEPLOYMENT.md - Setup guide
   - docs/RAG_DESIGN.md - Architecture

2. **Search Issues**: https://github.com/Copilot-Avaelgo/Team-2/issues

3. **Create New Issue**: Include:
   - Error message (full text)
   - Steps to reproduce
   - Environment (OS, Python version, etc.)
   - Logs from stderr/stdout

4. **Debug Locally First**: Most issues are local setup problems, not Azure/code issues

---

**Last Updated**: August 26, 2024
