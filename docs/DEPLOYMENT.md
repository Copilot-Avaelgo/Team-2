# Bona RAG System - Deployment Guide

## Prerequisites
- Azure subscription with credits
- Azure CLI installed (`az` command)
- GitHub account with push access to Team-2 repo
- Node.js 18+ (for frontend builds)
- Python 3.11+ (for backend builds)

## Step 1: Create Azure Resources

### Option A: Automated Setup (Recommended)
```bash
# Clone repo
git clone https://github.com/Copilot-Avaelgo/Team-2.git
cd Team-2

# Run setup script (Linux/Mac)
chmod +x deployment/azure-setup.sh
./deployment/azure-setup.sh

# On Windows, use Azure CLI directly (see Option B)
```

### Option B: Manual Setup (Azure CLI)
```bash
# Set variables
export RESOURCE_GROUP="bona-rag-rg"
export LOCATION="eastus"
export SEARCH_SERVICE="bona-search-$(date +%s)"
export APP_SERVICE="bona-api-$(date +%s)"
export STORAGE_ACCOUNT="bonastorage$(date +%s | tail -c 8)"

# 1. Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Create Cognitive Search (FREE tier)
az search service create \
  --name $SEARCH_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --sku free \
  --location $LOCATION

# 3. Create Storage Account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# 4. Create container
az storage container create \
  --name documents \
  --account-name $STORAGE_ACCOUNT

# 5. Create App Service Plan (Linux, B1 tier ~$12/month)
az appservice plan create \
  --name "bona-plan" \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

# 6. Create App Service
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan "bona-plan" \
  --name $APP_SERVICE \
  --runtime "PYTHON:3.11"

# 7. Create Static Web Apps for frontend (Free tier)
az staticwebapp create \
  --name "bona-frontend" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Free
```

## Step 2: Get Azure Credentials

```bash
# Get Cognitive Search API key
az search admin-key list \
  --resource-group $RESOURCE_GROUP \
  --service-name $SEARCH_SERVICE

# Get Storage Account key
az storage account keys list \
  --resource-group $RESOURCE_GROUP \
  --account-name $STORAGE_ACCOUNT

# Get Azure OpenAI credentials (already have from Azure OpenAI setup)
# AZURE_OPENAI_ENDPOINT format: https://your-resource.openai.azure.com/
# AZURE_OPENAI_API_KEY from Azure Portal
```

## Step 3: Configure GitHub Secrets

1. Go to: `https://github.com/Copilot-Avaelgo/Team-2/settings/secrets/actions`

2. Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `AZURE_OPENAI_API_KEY` | Your OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | https://your-resource.openai.azure.com/ |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | gpt-35-turbo |
| `AZURE_SEARCH_SERVICE_NAME` | $SEARCH_SERVICE |
| `AZURE_SEARCH_API_KEY` | From Cognitive Search |
| `AZURE_SEARCH_INDEX_NAME` | bona-products |
| `AZURE_STORAGE_ACCOUNT_NAME` | $STORAGE_ACCOUNT |
| `AZURE_STORAGE_ACCOUNT_KEY` | From Storage Account |
| `AZURE_APP_SERVICE_NAME` | $APP_SERVICE |
| `AZURE_PUBLISH_PROFILE` | (see step below) |
| `AZURE_STATIC_WEB_APPS_DEPLOYMENT_TOKEN` | (see step below) |

### Get App Service Publish Profile
```bash
az webapp deployment list-publishing-profiles \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE \
  --output json > publish-profile.json

# Copy contents of publish-profile.json as AZURE_PUBLISH_PROFILE secret
```

### Get Static Web Apps Deployment Token
```bash
az staticwebapp secrets list \
  --name "bona-frontend" \
  --resource-group $RESOURCE_GROUP

# Copy the deployment token as AZURE_STATIC_WEB_APPS_DEPLOYMENT_TOKEN
```

## Step 4: Initialize Cognitive Search Index

Before first deployment, create the search index:

```bash
# Option A: Via Python script (from backend folder)
python -c "
from src.services.document_processor import DocumentProcessor
from src.services.search_service import SearchService
from src.config import settings

processor = DocumentProcessor()
search = SearchService()

# Process documents from the ragf folder
docs = processor.load_and_process('../ragf')  # Adjust path as needed
search.index_documents(docs)
print(f'Indexed {len(docs)} document chunks')
"

# Option B: Manual via Azure Portal
# 1. Go to Azure Portal > Cognitive Search > Your service
# 2. Create index with name "bona-products"
# 3. Add fields: id (Edm.String, key), content (Edm.String, searchable), source (Edm.String, filterable)
```

## Step 5: Deploy (Automatic via GitHub Actions)

1. Commit and push to `main` branch:
```bash
git add .
git commit -m "Initial Bona RAG deployment"
git push origin main
```

2. GitHub Actions will automatically:
   - Build backend and frontend
   - Run tests (if present)
   - Deploy to Azure App Service (backend)
   - Deploy to Static Web Apps (frontend)

3. Monitor deployment:
   - Go to: `https://github.com/Copilot-Avaelgo/Team-2/actions`
   - Watch the `Build and Deploy` workflow

## Step 6: Verify Deployment

### Test Backend API
```bash
# Health check
curl https://$APP_SERVICE.azurewebsites.net/api/health

# Test chat endpoint
curl -X POST https://$APP_SERVICE.azurewebsites.net/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Bona Classic?"}'
```

### Access Frontend
```
https://bona-frontend-<hash>.azurestaticapps.net/
```

## Cost Monitoring

Check monthly Azure spend:
```bash
az cost management query create \
  --definition '{
    "type": "Usage",
    "timeframe": "MonthToDate",
    "dataset": {
      "granularity": "Daily",
      "aggregation": {
        "totalCost": {"name": "PreTaxCost", "function": "Sum"}
      }
    }
  }' \
  --scope "/subscriptions/<your-subscription-id>"
```

Expected costs:
- **App Service B1**: ~$12/month
- **Cognitive Search (Free)**: $0
- **Static Web Apps (Free)**: $0
- **Blob Storage**: ~$1-2/month
- **Azure OpenAI**: $5-20/month (~500 queries)
- **Total**: ~$18-35/month

## Scaling to Production

### If approaching resource limits:

#### Cognitive Search
- Free tier: 50 MB, 10k docs/day
- Upgrade to Standard tier: $15/month, 300 GB, 1M docs/day
```bash
az search service update \
  --resource-group $RESOURCE_GROUP \
  --name $SEARCH_SERVICE \
  --sku standard
```

#### App Service
- B1: 1 vCPU, 1.75 GB RAM
- Upgrade to B2: 2 vCPU, 3.5 GB RAM (~$48/month)
```bash
az appservice plan update \
  --name "bona-plan" \
  --resource-group $RESOURCE_GROUP \
  --sku B2
```

### Add Chat History
- Add Cosmos DB or PostgreSQL
- Implement session management
- See future phases in plan

## Troubleshooting

### Deployment Fails
```bash
# Check logs
az webapp log tail \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE

# Check deployment status
az webapp deployment list \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE
```

### API Returns 503
- RAG service not initialized
- Check environment variables are set
- Verify Azure credentials are correct

### Slow Responses
- Check Cognitive Search quota
- Monitor OpenAI API latency
- Consider caching for common queries

### Frontend Not Loading
- Check Static Web Apps deployment
- Clear browser cache
- Verify API endpoint in env variables

## Disaster Recovery

### Backup Documents
```bash
# Export Cognitive Search index
az search index export \
  --resource-group $RESOURCE_GROUP \
  --service-name $SEARCH_SERVICE \
  --index-name bona-products
```

### Restore from Backup
1. Delete current index
2. Re-process documents
3. Re-index to Cognitive Search

## Monitoring Setup (Optional)

Enable Application Insights for production:
```bash
az monitor app-insights component create \
  --app "bona-insights" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

Then add to backend `.env`:
```env
APPINSIGHTS_INSTRUMENTATION_KEY=<key-from-above>
```

## Next Steps
- Set up CI/CD alerts and notifications
- Configure Azure Backup policies
- Implement cost alerts in Azure Portal
- Plan scaling strategy based on usage metrics
