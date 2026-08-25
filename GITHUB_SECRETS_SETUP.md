# GitHub Actions Secrets Configuration

This guide shows exactly how to configure GitHub Actions secrets for Bona RAG System deployment.

## How to Add Secrets to GitHub

1. Go to your repository: https://github.com/Copilot-Avaelgo/Team-2
2. Click **Settings** (top navigation)
3. Click **Secrets and variables** > **Actions** (left sidebar)
4. Click **New repository secret** (green button)
5. Add each secret below with exact names and values

---

## Required Secrets

### Azure Subscription

**Name:** `AZURE_SUBSCRIPTION_ID`
**Value:** Your Azure subscription ID
**How to get:** 
```bash
az account show --query id -o tsv
```

**Name:** `AZURE_RESOURCE_GROUP`
**Value:** `bona-rag-rg` (or your chosen resource group name)

---

### Azure App Service (Backend API)

**Name:** `AZURE_APP_SERVICE_NAME`
**Value:** `bona-api-app` (or your chosen app service name)

---

### Azure Cognitive Search

**Name:** `AZURE_SEARCH_SERVICE_NAME`
**Value:** `bona-search` (or your chosen search service name)

**Name:** `AZURE_SEARCH_ADMIN_KEY`
**Value:** Your Cognitive Search admin key
**How to get:**
```bash
az search admin-key show \
  --resource-group bona-rag-rg \
  --service-name bona-search \
  --query 'primaryKey' -o tsv
```

**Name:** `AZURE_SEARCH_INDEX_NAME`
**Value:** `bona-documents`

---

### Azure Storage Account

**Name:** `AZURE_STORAGE_ACCOUNT_NAME`
**Value:** `bonaragstorage` (or your chosen storage account name)

**Name:** `AZURE_STORAGE_ACCOUNT_KEY`
**Value:** Your storage account key
**How to get:**
```bash
az storage account keys list \
  --account-name bonaragstorage \
  --resource-group bona-rag-rg \
  --query '[0].value' -o tsv
```

---

### Azure OpenAI

**Name:** `AZURE_OPENAI_ENDPOINT`
**Value:** `https://your-resource-name.openai.azure.com/`
**How to get:**
1. Go to https://portal.azure.com
2. Find your Azure OpenAI resource
3. Copy the "Endpoint" value from Overview page

**Name:** `AZURE_OPENAI_API_KEY`
**Value:** Your Azure OpenAI API key
**How to get:**
1. In Azure Portal, go to your OpenAI resource
2. Click "Keys and Endpoint" (left sidebar)
3. Copy "Key 1" or "Key 2"

**Name:** `AZURE_OPENAI_DEPLOYMENT_NAME`
**Value:** Name of your deployed model (e.g., `gpt-35-turbo`)
**How to get:**
1. In Azure Portal, go to your OpenAI resource
2. Click "Model deployments" (left sidebar)
3. Find your GPT-3.5-turbo deployment name

**Name:** `AZURE_OPENAI_MODEL_NAME`
**Value:** `gpt-3.5-turbo`

---

### Static Web Apps Deployment

**Name:** `AZURE_STATIC_WEB_APPS_API_TOKEN`
**Value:** Your Static Web Apps deployment token
**How to get:**
1. Go to https://portal.azure.com
2. Find your Static Web App resource
3. Click "Manage deployment token" (left sidebar)
4. Copy the token

---

## Verification Checklist

After adding all secrets, verify they're configured:

```bash
# ✅ Run these commands to verify secrets are accessible
# (You'll need to be authenticated to GitHub)

# Check that all required secrets exist
# Go to: GitHub repo > Settings > Secrets and variables > Actions

# Secrets to verify:
□ AZURE_SUBSCRIPTION_ID
□ AZURE_RESOURCE_GROUP
□ AZURE_APP_SERVICE_NAME
□ AZURE_SEARCH_SERVICE_NAME
□ AZURE_SEARCH_ADMIN_KEY
□ AZURE_SEARCH_INDEX_NAME
□ AZURE_STORAGE_ACCOUNT_NAME
□ AZURE_STORAGE_ACCOUNT_KEY
□ AZURE_OPENAI_ENDPOINT
□ AZURE_OPENAI_API_KEY
□ AZURE_OPENAI_DEPLOYMENT_NAME
□ AZURE_OPENAI_MODEL_NAME
□ AZURE_STATIC_WEB_APPS_API_TOKEN
```

---

## Testing the Secrets

After configuring all secrets, test the deployment:

```bash
# 1. Commit and push any changes
git add .
git commit -m "chore: configure secrets for deployment"

# 2. Push to main branch (triggers GitHub Actions)
git push origin main

# 3. Monitor the workflow
# Go to: GitHub repo > Actions tab
# Watch the "Deploy" workflow run

# 4. Check logs for any secret-related errors
# Each step shows detailed output
```

---

## Common Issues

### Secret not found error in GitHub Actions

**Problem:** Workflow fails with "secret AZURE_SEARCH_ADMIN_KEY not found"

**Solution:**
1. Verify exact secret name spelling (case-sensitive)
2. Make sure you added the secret to the correct repository (not organization secrets)
3. Re-add the secret if it was recently created
4. Refresh the page and try again

### Invalid credentials error

**Problem:** Workflow fails with "Invalid Azure credentials"

**Solution:**
1. Verify the secret value is correct (no extra spaces)
2. Get fresh credentials:
   ```bash
   # For admin key
   az search admin-key show --resource-group bona-rag-rg --service-name bona-search --query 'primaryKey' -o tsv
   
   # For storage key
   az storage account keys list --account-name bonaragstorage --resource-group bona-rag-rg --query '[0].value' -o tsv
   
   # For OpenAI key
   # (Only available in Azure Portal)
   ```
3. Update the secret with the fresh value

### Static Web Apps deployment fails

**Problem:** GitHub Actions fails at "Deploy to Static Web Apps" step

**Solution:**
1. Verify `AZURE_STATIC_WEB_APPS_API_TOKEN` is set correctly
2. Get new token from Azure Portal
3. Make sure Static Web App exists in same resource group
4. Check GitHub workflow has permission to deploy

---

## Security Best Practices

✅ **DO:**
- ✓ Use strong, unique values for all secrets
- ✓ Regenerate API keys periodically (every 90 days recommended)
- ✓ Review GitHub Actions logs for security issues
- ✓ Use branch protection rules to require approvals before deployment
- ✓ Audit secret access in GitHub

❌ **DON'T:**
- ✗ Commit secrets to git (even accidentally)
- ✗ Share secrets in comments, issues, or PRs
- ✗ Use the same secret value across multiple services
- ✗ Log secrets in GitHub Actions output
- ✗ Store secrets in .env files that are committed

---

## Next Steps

1. ✅ Add all secrets above to GitHub
2. ✅ Run `git push origin main` to trigger deployment
3. ✅ Monitor deployment at GitHub > Actions
4. ✅ Index documents with `python deployment/index-documents.py`
5. ✅ Test the chatbot at the deployed frontend URL

**Estimated time:** 15-20 minutes for full deployment
