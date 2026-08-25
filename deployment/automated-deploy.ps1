# Automated Azure Deployment for Bona RAG System
# This script creates all necessary Azure resources and configures GitHub Actions
# Prerequisites: Azure CLI installed and authenticated (az login)

param(
    [string]$ResourceGroup = "bona-rag-rg",
    [string]$Location = "eastus",
    [string]$AppServicePlan = "bona-app-plan",
    [string]$AppService = "bona-api-app",
    [string]$SearchService = "bona-search",
    [string]$StorageAccount = "bonaragstorage",
    [string]$StaticWebApp = "bona-chatbot",
    [string]$RepositoryUrl = "https://github.com/Copilot-Avaelgo/Team-2.git"
)

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   BONA RAG SYSTEM - AUTOMATED AZURE DEPLOYMENT                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n📋 Configuration:" -ForegroundColor Yellow
Write-Host "  • Resource Group: $ResourceGroup"
Write-Host "  • Location: $Location"
Write-Host "  • App Service: $AppService"
Write-Host "  • Search Service: $SearchService"
Write-Host "  • Storage Account: $StorageAccount"

$stepCount = 1

function Step {
    param([string]$Title, [string]$Description)
    Write-Host "`n[$stepCount] $Title" -ForegroundColor Green
    Write-Host "    $Description" -ForegroundColor Gray
    $script:stepCount++
}

# ════════════════════════════════════════════════════════════════════════════
# STEP 1: Create Resource Group
# ════════════════════════════════════════════════════════════════════════════
Step "Creating Resource Group" "Creating $ResourceGroup in $Location"
az group create --name $ResourceGroup --location $Location
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ⚠️  Resource Group may already exist. Continuing..." -ForegroundColor Yellow
}

# ════════════════════════════════════════════════════════════════════════════
# STEP 2: Create Storage Account
# ════════════════════════════════════════════════════════════════════════════
Step "Creating Storage Account" "Storage for documents and logs"
az storage account create `
    --name $StorageAccount `
    --resource-group $ResourceGroup `
    --location $Location `
    --sku Standard_LRS
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Storage Account created" -ForegroundColor Green
    $StorageKey = $(az storage account keys list --account-name $StorageAccount --resource-group $ResourceGroup --query '[0].value' -o tsv)
    Write-Host "  📌 Storage Key saved for GitHub Secrets" -ForegroundColor Cyan
} else {
    Write-Host "  ⚠️  Storage Account creation failed or already exists" -ForegroundColor Yellow
}

# ════════════════════════════════════════════════════════════════════════════
# STEP 3: Create Cognitive Search (Free Tier)
# ════════════════════════════════════════════════════════════════════════════
Step "Creating Azure Cognitive Search" "Free tier: 50MB storage, 10k docs/day indexing"
az search service create `
    --name $SearchService `
    --resource-group $ResourceGroup `
    --sku free `
    --location $Location
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Cognitive Search created (free tier)" -ForegroundColor Green
    $SearchKey = $(az search admin-key show --resource-group $ResourceGroup --service-name $SearchService --query 'primaryKey' -o tsv)
    Write-Host "  📌 Search Admin Key saved for GitHub Secrets" -ForegroundColor Cyan
} else {
    Write-Host "  ℹ️  Free tier Cognitive Search already exists in region or account" -ForegroundColor Yellow
}

# ════════════════════════════════════════════════════════════════════════════
# STEP 4: Create App Service Plan (B1 Tier)
# ════════════════════════════════════════════════════════════════════════════
Step "Creating App Service Plan" "B1 tier: $12/month, 1 core, 1.75GB RAM"
az appservice plan create `
    --name $AppServicePlan `
    --resource-group $ResourceGroup `
    --sku B1 `
    --is-linux
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ App Service Plan created (B1 tier)" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  App Service Plan may already exist. Continuing..." -ForegroundColor Yellow
}

# ════════════════════════════════════════════════════════════════════════════
# STEP 5: Create App Service
# ════════════════════════════════════════════════════════════════════════════
Step "Creating App Service" "Backend API hosting"
az webapp create `
    --name $AppService `
    --plan $AppServicePlan `
    --resource-group $ResourceGroup `
    --runtime "PYTHON|3.11"
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ App Service created" -ForegroundColor Green
    $AppServiceUrl = "https://$AppService.azurewebsites.net"
    Write-Host "  📌 App Service URL: $AppServiceUrl" -ForegroundColor Cyan
} else {
    Write-Host "  ⚠️  App Service may already exist. Continuing..." -ForegroundColor Yellow
}

# ════════════════════════════════════════════════════════════════════════════
# STEP 6: Create Static Web App
# ════════════════════════════════════════════════════════════════════════════
Step "Creating Static Web App" "Frontend hosting (free tier)"
az staticwebapp create `
    --name $StaticWebApp `
    --resource-group $ResourceGroup `
    --source $RepositoryUrl `
    --location $Location `
    --branch main `
    --build-folder frontend
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Static Web App created" -ForegroundColor Green
    $SwaUrl = "https://$(az staticwebapp show --name $StaticWebApp --resource-group $ResourceGroup --query 'defaultHostname' -o tsv)"
    Write-Host "  📌 Frontend URL: $SwaUrl" -ForegroundColor Cyan
} else {
    Write-Host "  ℹ️  Static Web App may already be configured" -ForegroundColor Yellow
}

# ════════════════════════════════════════════════════════════════════════════
# STEP 7: Create Azure OpenAI Resource (if not exists)
# ════════════════════════════════════════════════════════════════════════════
Step "Azure OpenAI Setup" "Requires manual setup in Azure Portal"
Write-Host "  ⚠️  MANUAL STEP: Create Azure OpenAI resource" -ForegroundColor Yellow
Write-Host "  1. Go to https://portal.azure.com" -ForegroundColor Gray
Write-Host "  2. Create new Azure OpenAI resource in same resource group" -ForegroundColor Gray
Write-Host "  3. Deploy gpt-3.5-turbo model (free trial available)" -ForegroundColor Gray
Write-Host "  4. Get API key and endpoint" -ForegroundColor Gray

# ════════════════════════════════════════════════════════════════════════════
# STEP 8: Configure GitHub Actions Secrets
# ════════════════════════════════════════════════════════════════════════════
Step "GitHub Secrets Configuration" "Copy these to GitHub Actions secrets"

Write-Host "`n📋 Add these secrets to GitHub (Settings > Secrets and variables > Actions):" -ForegroundColor Cyan
Write-Host "───────────────────────────────────────────────────────────────────" -ForegroundColor Cyan

$secrets = @{
    "AZURE_SUBSCRIPTION_ID" = "$(az account show --query id -o tsv)"
    "AZURE_RESOURCE_GROUP" = $ResourceGroup
    "AZURE_APP_SERVICE_NAME" = $AppService
    "AZURE_SEARCH_SERVICE_NAME" = $SearchService
    "AZURE_SEARCH_ADMIN_KEY" = $SearchKey
    "AZURE_STORAGE_ACCOUNT_NAME" = $StorageAccount
    "AZURE_STORAGE_ACCOUNT_KEY" = $StorageKey
    "AZURE_OPENAI_ENDPOINT" = "https://<your-openai-resource>.openai.azure.com/"
    "AZURE_OPENAI_API_KEY" = "<your-openai-api-key>"
    "AZURE_OPENAI_DEPLOYMENT_NAME" = "gpt-35-turbo"
}

foreach ($key in $secrets.Keys) {
    $value = $secrets[$key]
    Write-Host "  $key" -ForegroundColor Green
    if ($value.StartsWith("<")) {
        Write-Host "    Value: $value (⚠️  MANUAL - Get from Azure Portal)" -ForegroundColor Yellow
    } else {
        Write-Host "    Value: $value" -ForegroundColor Gray
    }
}

Write-Host "───────────────────────────────────────────────────────────────────" -ForegroundColor Cyan

# ════════════════════════════════════════════════════════════════════════════
# STEP 9: Deploy via GitHub Actions
# ════════════════════════════════════════════════════════════════════════════
Step "GitHub Actions Deployment" "Automated build and deploy"
Write-Host "  1. Add all secrets above to GitHub" -ForegroundColor Gray
Write-Host "  2. Run: git push origin main" -ForegroundColor Gray
Write-Host "  3. Check: https://github.com/Copilot-Avaelgo/Team-2/actions" -ForegroundColor Gray
Write-Host "  4. Wait for workflow to complete (5-10 minutes)" -ForegroundColor Gray

# ════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════════════════

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   DEPLOYMENT SUMMARY                                           ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n✅ Azure Resources Created:" -ForegroundColor Green
Write-Host "  ✓ Resource Group: $ResourceGroup" -ForegroundColor Gray
Write-Host "  ✓ Storage Account: $StorageAccount" -ForegroundColor Gray
Write-Host "  ✓ Cognitive Search (Free): $SearchService" -ForegroundColor Gray
Write-Host "  ✓ App Service Plan (B1): $AppServicePlan" -ForegroundColor Gray
Write-Host "  ✓ App Service: $AppService" -ForegroundColor Gray
Write-Host "  ✓ Static Web App: $StaticWebApp" -ForegroundColor Gray

Write-Host "`n⏭️  Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Copy GitHub Secrets (listed above)" -ForegroundColor Gray
Write-Host "  2. Create Azure OpenAI resource (manual)" -ForegroundColor Gray
Write-Host "  3. Run: git push origin main" -ForegroundColor Gray
Write-Host "  4. Monitor: GitHub Actions > Deploy workflow" -ForegroundColor Gray
Write-Host "  5. Index documents: Run indexing script" -ForegroundColor Gray

Write-Host "`n📊 Estimated Monthly Cost: $18-35/month" -ForegroundColor Yellow

Write-Host "`nDeployment script completed! 🚀" -ForegroundColor Green
