#!/bin/bash

# Azure Setup Script for Bona RAG System
# This script creates all necessary Azure resources

set -e

echo "🔧 Bona RAG - Azure Resource Setup"
echo "===================================="
echo ""

# Variables
RESOURCE_GROUP=${1:-"bona-rag-rg"}
LOCATION=${2:-"eastus"}
SEARCH_SERVICE=${3:-"bona-search"}
APP_SERVICE_PLAN=${4:-"bona-plan"}
APP_SERVICE=${5:-"bona-api"}
STORAGE_ACCOUNT=${6:-"bonastorage"}
COGNITIVE_SEARCH_TIER=${7:-"free"}

echo "📋 Resource Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Search Service: $SEARCH_SERVICE"
echo "  App Service: $APP_SERVICE"
echo "  Storage Account: $STORAGE_ACCOUNT"
echo ""

# Create resource group
echo "✅ Creating resource group..."
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION"

# Create Cognitive Search
echo "✅ Creating Azure Cognitive Search..."
az search service create \
  --name "$SEARCH_SERVICE" \
  --resource-group "$RESOURCE_GROUP" \
  --sku "$COGNITIVE_SEARCH_TIER" \
  --location "$LOCATION"

# Create Storage Account
echo "✅ Creating Azure Blob Storage..."
az storage account create \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku Standard_LRS

# Create container
az storage container create \
  --name documents \
  --account-name "$STORAGE_ACCOUNT"

# Create App Service Plan
echo "✅ Creating App Service Plan..."
az appservice plan create \
  --name "$APP_SERVICE_PLAN" \
  --resource-group "$RESOURCE_GROUP" \
  --sku B1 \
  --is-linux

# Create App Service
echo "✅ Creating App Service for backend..."
az webapp create \
  --resource-group "$RESOURCE_GROUP" \
  --plan "$APP_SERVICE_PLAN" \
  --name "$APP_SERVICE" \
  --runtime "PYTHON:3.11"

echo ""
echo "✨ Azure Resources Created Successfully!"
echo ""
echo "📝 Next Steps:"
echo "1. Configure GitHub Secrets with Azure credentials:"
echo "   - AZURE_OPENAI_API_KEY"
echo "   - AZURE_OPENAI_ENDPOINT"
echo "   - AZURE_OPENAI_DEPLOYMENT_NAME"
echo "   - AZURE_SEARCH_SERVICE_NAME: $SEARCH_SERVICE"
echo "   - AZURE_SEARCH_API_KEY"
echo "   - AZURE_STORAGE_ACCOUNT_NAME: $STORAGE_ACCOUNT"
echo "   - AZURE_STORAGE_ACCOUNT_KEY"
echo ""
echo "2. Get API keys:"
echo "   az search admin-key list --resource-group $RESOURCE_GROUP --service-name $SEARCH_SERVICE"
echo "   az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_ACCOUNT"
echo ""
