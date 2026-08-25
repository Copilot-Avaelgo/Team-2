# BONA RAG SYSTEM - DEPLOYMENT CHECKLIST

> **Status**: ✅ Ready for Automated Deployment  
> **Version**: 1.0  
> **Last Updated**: 2026-08-26

## Pre-Deployment Verification

- [ ] Azure subscription is active and accessible
- [ ] Azure CLI is installed: `az --version`
- [ ] You are authenticated: `az login`
- [ ] Python 3.8+ installed for document indexing
- [ ] Git repository cloned and up-to-date

---

## Phase 1: Azure Resource Deployment (30 minutes)

### Option A: Automated Script (Recommended)

```powershell
# 1. Open PowerShell as Administrator
# 2. Navigate to repo
cd D:\AI2\Team-2

# 3. Verify Azure CLI installed
az --version

# 4. Login to Azure (opens browser for authentication)
az login

# 5. Run automated deployment script
.\deployment\automated-deploy.ps1
```

**What this does:**
- Creates Resource Group: `bona-rag-rg`
- Creates Storage Account: `bonaragstorage`
- Creates Cognitive Search (Free tier): `bona-search`
- Creates App Service Plan (B1): `bona-app-plan`
- Creates App Service: `bona-api-app`
- Creates Static Web App: `bona-chatbot`
- Outputs all credentials needed for GitHub Secrets

**Expected time:** 10-15 minutes

**Success indicators:**
- ✅ All resources created successfully
- ✅ Output shows Azure resource URLs
- ✅ Credentials displayed for GitHub Secrets

---

### Option B: Manual Azure Portal

If script fails, use Azure Portal:

1. **Resource Group**
   - Name: `bona-rag-rg`
   - Location: `East US` (or your preference)

2. **Storage Account**
   - Name: `bonaragstorage`
   - Performance: Standard
   - Replication: LRS
   - Region: Same as resource group

3. **Azure Cognitive Search**
   - Name: `bona-search`
   - Pricing Tier: Free (50MB, 10k docs/day)
   - Region: Same as resource group
   - **Important:** Only 1 free tier per subscription

4. **App Service Plan**
   - Name: `bona-app-plan`
   - OS: Linux
   - Pricing tier: B1 ($12/month)

5. **App Service**
   - Name: `bona-api-app`
   - Runtime: Python 3.11
   - Plan: `bona-app-plan`
   - Region: Same as resource group

6. **Static Web App**
   - Name: `bona-chatbot`
   - Region: Same as resource group
   - Connect to GitHub (you'll need to authorize)
   - Repository: Team-2
   - Branch: main

7. **Azure OpenAI** (MANUAL SETUP REQUIRED)
   - Name: `bona-openai`
   - Model: gpt-3.5-turbo
   - Region: East US (or applicable region)
   - **Get these from Azure Portal:**
     - Endpoint: Copy from "Keys and Endpoint" page
     - API Key: Copy from "Keys and Endpoint" page
     - Deployment Name: Name of your model deployment

---

## Phase 2: GitHub Secrets Configuration (10 minutes)

After Azure resources are created, gather these values:

### From Azure Portal

1. **Subscription ID**
   ```bash
   az account show --query id -o tsv
   ```

2. **Cognitive Search Admin Key**
   ```bash
   az search admin-key show \
     --resource-group bona-rag-rg \
     --service-name bona-search \
     --query 'primaryKey' -o tsv
   ```

3. **Storage Account Key**
   ```bash
   az storage account keys list \
     --account-name bonaragstorage \
     --resource-group bona-rag-rg \
     --query '[0].value' -o tsv
   ```

4. **Azure OpenAI Values** (From Azure Portal)
   - Go to your OpenAI resource > "Keys and Endpoint"
   - Copy: Endpoint, Key 1 (or Key 2)
   - Go to "Model deployments" > note deployment name

### Add to GitHub

1. Go to: https://github.com/Copilot-Avaelgo/Team-2/settings/secrets/actions
2. Click "New repository secret"
3. Add these 13 secrets:

| Secret Name | Value | Source |
|---|---|---|
| `AZURE_SUBSCRIPTION_ID` | Your subscription ID | `az account show --query id` |
| `AZURE_RESOURCE_GROUP` | `bona-rag-rg` | Azure Portal |
| `AZURE_APP_SERVICE_NAME` | `bona-api-app` | Azure Portal |
| `AZURE_SEARCH_SERVICE_NAME` | `bona-search` | Azure Portal |
| `AZURE_SEARCH_ADMIN_KEY` | Admin key value | Command above |
| `AZURE_SEARCH_INDEX_NAME` | `bona-documents` | Fixed value |
| `AZURE_STORAGE_ACCOUNT_NAME` | `bonaragstorage` | Azure Portal |
| `AZURE_STORAGE_ACCOUNT_KEY` | Storage key value | Command above |
| `AZURE_OPENAI_ENDPOINT` | `https://xxx.openai.azure.com/` | Azure Portal |
| `AZURE_OPENAI_API_KEY` | Your OpenAI API key | Azure Portal |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | `gpt-35-turbo` | Azure Portal |
| `AZURE_OPENAI_MODEL_NAME` | `gpt-3.5-turbo` | Fixed value |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Deployment token | Azure Portal |

---

## Phase 3: GitHub Actions Deployment (10-15 minutes)

### Trigger Deployment

```bash
# 1. Navigate to repo
cd D:\AI2\Team-2

# 2. Verify all changes are committed
git status

# 3. Push to main (triggers GitHub Actions)
git push origin main
```

### Monitor Deployment

1. Go to: https://github.com/Copilot-Avaelgo/Team-2/actions
2. Click the "Deploy" workflow run
3. Watch these steps complete:
   - ✅ Checkout code
   - ✅ Set up Python
   - ✅ Install backend dependencies
   - ✅ Run backend tests
   - ✅ Build Docker image
   - ✅ Set up Node.js
   - ✅ Install frontend dependencies
   - ✅ Run frontend tests
   - ✅ Build frontend (Vite)
   - ✅ Deploy backend to App Service
   - ✅ Deploy frontend to Static Web Apps

**Expected time:** 10-15 minutes  
**Success indicators:**
- ✅ All workflow steps pass (green checkmarks)
- ✅ No "credentials not found" errors
- ✅ Deployment logs show successful push to Azure

---

## Phase 4: Document Indexing (10 minutes)

After deployment completes, index your Bona TDS documents:

```bash
# 1. Install Azure SDK dependencies
pip install azure-search-documents azure-identity

# 2. Run indexing script
python deployment/index-documents.py \
  --service-name bona-search \
  --admin-key <AZURE_SEARCH_ADMIN_KEY> \
  --docs-path ./ragf

# Or use environment variables
export AZURE_SEARCH_SERVICE_NAME=bona-search
export AZURE_SEARCH_ADMIN_KEY=<your-key>
python deployment/index-documents.py
```

**What this does:**
- Reads all `.txt` files from `./ragf/` folder (Bona TDS files)
- Chunks documents into 500-word segments with 100-word overlap
- Uploads ~200-300 chunks to Cognitive Search
- Makes documents searchable for the RAG pipeline

**Expected time:** 2-5 minutes  
**Success indicators:**
- ✅ Script shows "Successfully indexed X chunks"
- ✅ No errors during upload
- ✅ Azure Portal shows updated document count

---

## Phase 5: Verification (10 minutes)

### Test Backend API

```bash
# Get your app service URL
# Format: https://bona-api-app.azurewebsites.net

# Test health endpoint
curl https://bona-api-app.azurewebsites.net/api/health

# Expected response:
# {"status": "healthy", "services": {"search": "healthy", "llm": "healthy"}}
```

### Test Frontend

1. Get your Static Web App URL from Azure Portal
2. Open in browser: `https://bona-chatbot-xxxx.azurestaticapps.net/`
3. Try a test query: "What is Bona Classic?"
4. Verify:
   - ✅ Message appears in chat
   - ✅ Loading indicator shows
   - ✅ Response appears from backend
   - ✅ Sources are displayed

### Test Chat Flow

1. Type: "What is the drying time for Bona Classic?"
2. Verify:
   - ✅ Chat shows your message
   - ✅ Bot shows "typing..." indicator
   - ✅ Response appears within 5 seconds
   - ✅ Response includes product information
   - ✅ Sources from TDS files are shown
   - ✅ No error messages

---

## Cost Verification

Check Azure costs:

```bash
# Get current cost estimate
az costmanagement query create \
  --scope /subscriptions/<SUBSCRIPTION_ID> \
  --timeframe MonthToDate \
  --type Usage
```

**Expected monthly cost:** $18-35 (under $50 budget)
- Cognitive Search (free): $0
- Static Web Apps (free): $0
- App Service B1: $12-15
- Blob Storage: $1-2
- Azure OpenAI (pay per token): $5-20

---

## Troubleshooting

### Issue: Azure CLI command fails

```bash
# Verify authentication
az account show

# If not authenticated, login again
az login

# List available subscriptions
az account list --output table
```

### Issue: GitHub Actions workflow fails

Check workflow logs:
1. Go to Actions tab
2. Click failed workflow
3. Expand failed step
4. Look for error messages
5. Common causes:
   - Secret not found (check spelling)
   - Invalid credentials (regenerate in Azure Portal)
   - Resource already exists (delete and retry)

### Issue: Documents not indexed

```bash
# Verify credentials work
az search admin-key show \
  --resource-group bona-rag-rg \
  --service-name bona-search

# Check if documents exist in search service
# (Use Azure Portal > Cognitive Search > Indexes)

# Manually test indexing with smaller file
python deployment/index-documents.py --docs-path ./ragf
```

### Issue: Chatbot returns empty responses

1. Verify documents are indexed:
   - Azure Portal > Cognitive Search > bona-documents index
   - Should show "X documents"
   
2. Verify search works:
   ```bash
   # Query search service
   curl -X POST "https://bona-search.search.windows.net/indexes/bona-documents/docs/search?api-version=2023-07-01-Preview" \
     -H "Content-Type: application/json" \
     -H "api-key: <ADMIN_KEY>" \
     -d '{"search": "Bona Classic"}'
   ```

3. Check OpenAI configuration:
   - Verify deployment name matches
   - Verify API key is valid
   - Check Azure OpenAI quota

---

## Success Checklist

After all phases complete, verify:

- [ ] ✅ All 4 Azure resources created successfully
- [ ] ✅ All 13 GitHub Secrets configured
- [ ] ✅ GitHub Actions workflow completed successfully
- [ ] ✅ ~200+ Bona TDS chunks indexed in Cognitive Search
- [ ] ✅ Backend API responds to health check
- [ ] ✅ Frontend loads in browser
- [ ] ✅ Chat sends messages successfully
- [ ] ✅ Responses include product information
- [ ] ✅ Sources are displayed correctly
- [ ] ✅ Monthly cost is under $50

---

## Next Steps After Deployment

1. **Monitor Performance**
   - Set up Application Insights (optional, $0-10/month)
   - Monitor error rates and response times
   - Review chatbot usage analytics

2. **Optimize Documents**
   - Review chat logs to see which products users ask about
   - Add more detailed TDS chunks for popular products
   - Remove obsolete product documentation

3. **Improve Responses**
   - Fine-tune system prompt in `llm_service.py`
   - Adjust chunk size/overlap if needed
   - Add more specific product categories

4. **Scale Up** (if needed)
   - Upgrade App Service from B1 to B2 ($25/month)
   - Upgrade Cognitive Search to Standard tier ($250+/month)
   - Add caching layer (Redis, $15-50/month)
   - Set up CDN for frontend (free with SWA)

---

## Support & Documentation

- **API Reference:** `docs/API.md` (endpoint details, parameters)
- **RAG Architecture:** `docs/RAG_DESIGN.md` (how RAG pipeline works)
- **Troubleshooting:** `docs/TROUBLESHOOTING.md` (common issues)
- **Cost Analysis:** `cost_analysis.md` (detailed cost breakdown)
- **Quick Deploy:** `QUICK_DEPLOY.md` (5-minute version)

---

**Status: 🟢 READY FOR DEPLOYMENT**

Start with Phase 1 (Azure resources) and follow each phase in order.  
Expected total time: **1.5-2 hours**
