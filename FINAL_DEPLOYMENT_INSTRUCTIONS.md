# FINAL DEPLOYMENT GUIDE - BONA RAG SYSTEM

> **Status**: 🟢 Ready for Production Deployment  
> **Authentication**: ✅ Azure CLI Already Authenticated  
> **Subscription**: AI Sponsorship 6K FiscalYear2025  
> **User**: catalin.sfredel@avaelgo.ro

---

## ⚠️ IMPORTANT: Permission Issue

Your Azure account is authenticated but lacks write permissions on the current subscription. This is a **security restriction**, not an error.

### Two Solutions:

**Option A: Request Elevated Permissions** (Recommended for team use)
1. Contact your Azure subscription administrator
2. Request "Contributor" role on subscription `89d9a867-b5fe-4989-aaec-504f4c698ba2`
3. Once granted, re-run deployment scripts

**Option B: Use Azure Portal UI** (Fastest for single deployment)
1. Go to https://portal.azure.com
2. Manually create 7 resources (30 minutes, see checklist below)
3. Configure GitHub Secrets
4. Push to main branch for automatic deployment

---

## OPTION B: Manual Azure Portal Deployment (Recommended)

### Step 1: Create Resource Group (2 minutes)

1. Go to https://portal.azure.com
2. Search: **"Resource groups"**
3. Click **"Create"**
   - Name: `bona-rag-rg`
   - Region: `East US` (or your preference)
4. Click **"Review + Create"** → **"Create"**
5. Wait for "Deployment complete" notification

### Step 2: Create Storage Account (3 minutes)

1. Go to https://portal.azure.com
2. Search: **"Storage accounts"**
3. Click **"Create"**
   - Subscription: Your current subscription
   - Resource Group: `bona-rag-rg` (created above)
   - Storage account name: `bonaragstorage`
   - Region: Same as resource group
   - Performance: Standard
   - Replication: Locally-redundant storage (LRS)
4. Click **"Review + Create"** → **"Create"**
5. Go to resource when deployment completes
6. **SAVE KEY FOR LATER:**
   - Click **"Access keys"** (left sidebar)
   - Copy **"Key1"** value
   - Save as: `AZURE_STORAGE_ACCOUNT_KEY`

### Step 3: Create Azure Cognitive Search (3 minutes)

1. Go to https://portal.azure.com
2. Search: **"Azure Cognitive Search"**
3. Click **"Create"**
   - Subscription: Your current subscription
   - Resource Group: `bona-rag-rg`
   - Service name: `bona-search`
   - Region: Same as resource group
   - **Pricing tier: Free** (50MB, 10k docs/day - sufficient for MVP)
4. Click **"Review + Create"** → **"Create"**
5. Go to resource when deployment completes
6. **SAVE KEY FOR LATER:**
   - Click **"Keys"** (left sidebar under "Settings")
   - Copy **"Primary admin key"**
   - Save as: `AZURE_SEARCH_ADMIN_KEY`

### Step 4: Create App Service Plan (2 minutes)

1. Go to https://portal.azure.com
2. Search: **"App Service plans"**
3. Click **"Create"**
   - Subscription: Your current subscription
   - Resource Group: `bona-rag-rg`
   - Name: `bona-app-plan`
   - OS: **Linux** (important!)
   - Region: Same as resource group
   - Pricing tier: **B1** ($12/month)
4. Click **"Review + Create"** → **"Create"**

### Step 5: Create App Service (2 minutes)

1. Go to https://portal.azure.com
2. Search: **"App Services"**
3. Click **"Create"** → **"Web App"**
   - Subscription: Your current subscription
   - Resource Group: `bona-rag-rg`
   - Name: `bona-api-app`
   - Publish: **Code**
   - Runtime stack: **Python 3.11**
   - Operating System: **Linux**
   - App Service Plan: `bona-app-plan` (created above)
4. Click **"Review + Create"** → **"Create"**
5. Go to resource when deployment completes
6. **SAVE URL FOR LATER:**
   - Copy URL from top (format: `https://bona-api-app.azurewebsites.net`)
   - Save as: `API_URL`

### Step 6: Create Azure OpenAI Resource (5 minutes) - MANUAL

1. Go to https://portal.azure.com
2. Search: **"Azure OpenAI"**
3. Click **"Create"**
   - Subscription: Your current subscription
   - Resource Group: `bona-rag-rg`
   - Region: **East US** (only region with GPT-3.5-turbo availability)
   - Name: `bona-openai`
   - Pricing tier: Standard S0
4. Click **"Review + Create"** → **"Create"**
5. Go to resource when deployment completes
6. **Deploy Model:**
   - Click **"Model deployments"** (left sidebar, under "Resource Management")
   - Click **"Manage Deployments"** (opens Azure OpenAI Studio)
   - Click **"Create new deployment"**
     - Model: **gpt-3.5-turbo**
     - Model version: Default (latest)
     - Deployment name: **gpt-35-turbo** (exactly this)
     - Capacity: 1 (default)
   - Click **"Create"**
7. **SAVE KEYS FOR LATER:**
   - Go back to Azure Portal > Your OpenAI resource
   - Click **"Keys and Endpoint"** (left sidebar)
   - Copy:
     - **Endpoint**: `https://xxx.openai.azure.com/`
     - **Key 1** or **Key 2**
   - Save as: `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY`

### Step 7: Create Static Web App (3 minutes)

1. Go to https://portal.azure.com
2. Search: **"Static Web Apps"**
3. Click **"Create"**
   - Subscription: Your current subscription
   - Resource Group: `bona-rag-rg`
   - Name: `bona-chatbot`
   - Region: Same as resource group
   - Source: **GitHub** (connects repo)
   - Organization: Select yours
   - Repository: **Team-2**
   - Branch: **main**
   - Build presets: **React**
   - App location: `frontend`
   - API location: (leave blank)
   - Output location: `dist`
4. Click **"Review + Create"** → **"Create"**
5. Authorize GitHub access when prompted
6. **SAVE TOKEN FOR LATER:**
   - Go to resource when deployment completes
   - Click **"Manage deployment token"** (left sidebar)
   - Copy the token
   - Save as: `AZURE_STATIC_WEB_APPS_API_TOKEN`

---

## GITHUB SECRETS CONFIGURATION (10 minutes)

Now that all Azure resources are created, add secrets to GitHub:

### Get All Required Values

Open a PowerShell window and run:

```powershell
# Get Subscription ID
az account show --query id -o tsv

# Get Storage Account Key
az storage account keys list `
  --account-name bonaragstorage `
  --resource-group bona-rag-rg `
  --query '[0].value' -o tsv

# Get Cognitive Search Admin Key
az search admin-key show `
  --resource-group bona-rag-rg `
  --service-name bona-search `
  --query 'primaryKey' -o tsv
```

### Add Secrets to GitHub

1. Go to: https://github.com/Copilot-Avaelgo/Team-2/settings/secrets/actions
2. Click **"New repository secret"** for each of these:

| Secret Name | Value | Example |
|---|---|---|
| `AZURE_SUBSCRIPTION_ID` | From `az account show` | `89d9a867-b5fe-4989-aaec-504f4c698ba2` |
| `AZURE_RESOURCE_GROUP` | Resource group name | `bona-rag-rg` |
| `AZURE_APP_SERVICE_NAME` | App service name | `bona-api-app` |
| `AZURE_SEARCH_SERVICE_NAME` | Search service name | `bona-search` |
| `AZURE_SEARCH_ADMIN_KEY` | From `az search admin-key show` | `xyz...` |
| `AZURE_SEARCH_INDEX_NAME` | Index name | `bona-documents` |
| `AZURE_STORAGE_ACCOUNT_NAME` | Storage account name | `bonaragstorage` |
| `AZURE_STORAGE_ACCOUNT_KEY` | From `az storage account keys list` | `key...` |
| `AZURE_OPENAI_ENDPOINT` | From Azure Portal | `https://xxx.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | From Azure Portal Keys page | `key...` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Model deployment name | `gpt-35-turbo` |
| `AZURE_OPENAI_MODEL_NAME` | Model name | `gpt-3.5-turbo` |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | From SWA Portal | `token...` |

✅ **Total:** 13 secrets configured

---

## DEPLOYMENT TO AZURE (5 minutes)

Once all secrets are added:

```bash
# 1. Navigate to repo
cd D:\AI2\Team-2

# 2. Verify all changes staged
git status

# 3. Push to main (triggers GitHub Actions)
git push origin main
```

### Monitor Deployment

1. Go to: https://github.com/Copilot-Avaelgo/Team-2/actions
2. Click the "Deploy" workflow
3. Watch these steps:
   - ✅ Checkout code
   - ✅ Set up Python
   - ✅ Run backend tests
   - ✅ Build Docker image
   - ✅ Set up Node.js
   - ✅ Run frontend tests
   - ✅ Build React frontend
   - ✅ Deploy to App Service (backend)
   - ✅ Deploy to Static Web App (frontend)

**Expected time:** 10-15 minutes  
**Status:** All steps should have green checkmarks

---

## DOCUMENT INDEXING (5 minutes)

After deployment completes:

```powershell
# 1. Navigate to repo
cd D:\AI2\Team-2

# 2. Install Azure SDK
pip install azure-search-documents azure-identity

# 3. Set environment variables
$env:AZURE_SEARCH_SERVICE_NAME = "bona-search"
$env:AZURE_SEARCH_ADMIN_KEY = "your-admin-key-from-github-secrets"

# 4. Run indexing
python deployment/index-documents.py
```

**Expected output:**
```
✅ Successfully indexed 250+ chunks from 17 documents
```

---

## VERIFICATION (5 minutes)

### Test Backend API

```powershell
# Health check
curl https://bona-api-app.azurewebsites.net/api/health

# Expected response:
# {"status":"healthy","services":{"search":"healthy","llm":"healthy"}}
```

### Test Frontend

1. Open browser: https://bona-chatbot-xxxx.azurestaticapps.net/
2. Try chat: "What is Bona Classic?"
3. Verify:
   - ✅ Message appears
   - ✅ Loading indicator shows
   - ✅ Response appears within 5 seconds
   - ✅ Sources are displayed

---

## COST VERIFICATION

Check your Azure Portal:

**Expected monthly costs:**
- Cognitive Search (free tier): **$0**
- Static Web App (free): **$0**
- App Service B1: **$12-15**
- Storage: **$1-2**
- Azure OpenAI (pay-per-token): **$5-20**

**Total: $18-35/month** ✅ Well under $50 budget

---

## COMPLETE AUTOMATION (If permissions granted later)

If your Azure administrator grants you contributor access, you can use this one-line deployment:

```powershell
cd D:\AI2\Team-2
.\deployment\automated-deploy.ps1
```

This will automatically:
- Create all 6 Azure resources
- Retrieve all credentials
- Display GitHub Secrets format
- Ready for GitHub Actions deployment

---

## TROUBLESHOOTING

### "Deployment step failed"
→ Check GitHub Actions logs > failed step > error message
→ Usually: Secret not configured or invalid value

### "Static Web App deployment fails"
→ Verify `AZURE_STATIC_WEB_APPS_API_TOKEN` is correct
→ Get new token from Azure Portal > Static Web App > Manage deployment token

### "Chat returns empty responses"
→ Verify documents indexed: `python deployment/index-documents.py`
→ Check Cognitive Search: Portal > bona-search > Indexes > bona-documents

### "OpenAI API errors"
→ Verify deployment name is exactly `gpt-35-turbo`
→ Check API key is valid (regenerate in Portal if needed)
→ Verify model is deployed (go to Azure OpenAI Studio)

---

## NEXT STEPS

✅ Step 1: Create 7 Azure resources using Azure Portal (30 min)  
✅ Step 2: Add 13 GitHub Secrets (10 min)  
✅ Step 3: Push to main branch (5 min)  
✅ Step 4: Monitor GitHub Actions deployment (10 min)  
✅ Step 5: Index documents (5 min)  
✅ Step 6: Test in browser (5 min)  

**Total time: ~1.5 hours | Budget used: ~$20/month**

---

**Ready to deploy! 🚀**
