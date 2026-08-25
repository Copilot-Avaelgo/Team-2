# ⚡ QUICK DEPLOYMENT CARD - Bona RAG System

**Status**: Ready to deploy  
**Time**: 1.5-2 hours  
**Cost**: $18-35/month  

---

## 🚀 CREATE 7 AZURE RESOURCES

Go to: https://portal.azure.com

### 1️⃣ RESOURCE GROUP
- Name: `bona-rag-rg`
- Region: `East US`
- **Status**: ✅ Create first

### 2️⃣ STORAGE ACCOUNT
- Name: `bonaragstorage`
- Resource Group: `bona-rag-rg`
- Replication: LRS
- **SAVE**: Access Key → `AZURE_STORAGE_ACCOUNT_KEY`

### 3️⃣ COGNITIVE SEARCH (Free Tier!)
- Name: `bona-search`
- Resource Group: `bona-rag-rg`
- **Pricing: FREE TIER** (important!)
- **SAVE**: Admin Key → `AZURE_SEARCH_ADMIN_KEY`

### 4️⃣ APP SERVICE PLAN
- Name: `bona-app-plan`
- Resource Group: `bona-rag-rg`
- OS: **Linux** (important!)
- Tier: **B1** ($12/month)

### 5️⃣ APP SERVICE
- Name: `bona-api-app`
- Resource Group: `bona-rag-rg`
- Runtime: **Python 3.11**
- Plan: `bona-app-plan`

### 6️⃣ STATIC WEB APP
- Name: `bona-chatbot`
- Resource Group: `bona-rag-rg`
- **SAVE**: Deployment Token → `AZURE_STATIC_WEB_APPS_API_TOKEN`

### 7️⃣ AZURE OPENAI
- Name: `bona-openai`
- Resource Group: `bona-rag-rg`
- Model: `gpt-3.5-turbo` (deployment name)
- **SAVE**: API Key → `AZURE_OPENAI_API_KEY`
- **SAVE**: Endpoint → `AZURE_OPENAI_ENDPOINT`

---

## 📋 SAVE THESE VALUES

Create a text file with all credentials:

```
AZURE_OPENAI_API_KEY = <from OpenAI resource>
AZURE_OPENAI_ENDPOINT = https://<your-openai>.openai.azure.com/
AZURE_SEARCH_ADMIN_KEY = <from Cognitive Search>
AZURE_SEARCH_SERVICE_NAME = bona-search
AZURE_STORAGE_ACCOUNT_KEY = <from Storage Account>
AZURE_STORAGE_ACCOUNT_NAME = bonaragstorage
AZURE_RESOURCE_GROUP = bona-rag-rg
AZURE_APP_SERVICE_NAME = bona-api-app
AZURE_STATIC_WEB_APPS_API_TOKEN = <from Static Web App>
```

---

## 🔐 ADD GITHUB SECRETS

After all 7 resources created:

1. Go to: https://github.com/Copilot-Avaelgo/Team-2/settings/secrets/actions
2. Create 13 new secrets (copy values from above)
3. See `GITHUB_SECRETS_SETUP.md` for exact names

**Required Secrets:**
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT_NAME` (value: `gpt-35-turbo`)
- `AZURE_SEARCH_ADMIN_KEY`
- `AZURE_SEARCH_SERVICE_NAME`
- `AZURE_STORAGE_ACCOUNT_KEY`
- `AZURE_STORAGE_ACCOUNT_NAME`
- `AZURE_RESOURCE_GROUP`
- `AZURE_APP_SERVICE_NAME`
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `DOCKER_REGISTRY`
- Plus others in reference doc

---

## 🚀 DEPLOY

After all secrets added:

```bash
cd D:\AI2\Team-2
git push origin main
```

GitHub Actions automatically:
- ✅ Builds backend
- ✅ Builds frontend
- ✅ Runs tests
- ✅ Deploys to Azure

Monitor: https://github.com/Copilot-Avaelgo/Team-2/actions

---

## 📚 INDEX DOCUMENTS

After GitHub Actions completes:

```bash
python deployment/index-documents.py \
  --service-name bona-search \
  --admin-key <AZURE_SEARCH_ADMIN_KEY>
```

This uploads 17 Bona TDS files to search index.

---

## ✅ VERIFY DEPLOYMENT

### Health Check
```bash
curl https://bona-api-app.azurewebsites.net/api/health
```
Should return: `{"status": "ok"}`

### Chat Test
1. Open: https://bona-chatbot-xxxx.azurestaticapps.net/
2. Type: "What is Bona Classic?"
3. Should get response with source documents

---

## 🎯 EXPECTED TIMELINE

| Step | Time | Cumulative |
|------|------|------------|
| Create resources | 30 min | 30 min |
| Add GitHub secrets | 10 min | 40 min |
| Deploy via GitHub | 5 min | 45 min |
| Index documents | 5 min | 50 min |
| Verify & test | 5 min | 55 min |
| **TOTAL** | | **~1 hour** |

---

## 📞 IF ISSUES

**Common problems:**
- Resource name taken? → Use `bona-rag-rg2` or add timestamp
- Free tier limit? → Use Basic tier instead
- No Static Web App region? → Use default region
- OpenAI not available? → Check region availability

See: `docs/TROUBLESHOOTING.md` for detailed solutions

---

## ✨ YOU'RE READY!

All code is complete. All tests passing. Just create 7 resources and push code. System goes live immediately.

**Questions?** Check `DEPLOYMENT_CHECKLIST.md` or `START_HERE.md`

