# Bona RAG System - Product Support Assistant

A cost-optimized RAG (Retrieval-Augmented Generation) chatbot for Bona flooring products, built with React + FastAPI + Azure services.

## 🎯 Quick Start

### Prerequisites
- Azure subscription with free credits
- GitHub account
- Node.js 18+ and Python 3.11+

### 5-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/Copilot-Avaelgo/Team-2.git
cd Team-2

# 2. Create Azure resources (see docs/DEPLOYMENT.md)
# 3. Add GitHub Secrets (see docs/DEPLOYMENT.md)
# 4. Push to main branch
git push origin main

# 5. GitHub Actions will deploy automatically
# Monitor at: https://github.com/Copilot-Avaelgo/Team-2/actions
```

## 📋 Features

- ✅ **Chat Interface**: Modern, responsive UI matching Bona branding
- ✅ **RAG-Powered**: Retrieves product docs for accurate answers
- ✅ **Source Attribution**: Shows which TDS sheets were used
- ✅ **Free Tier**: Runs on Azure free resources (~$18-35/month)
- ✅ **CI/CD**: Automatic deployment via GitHub Actions
- ✅ **Scalable**: Easy upgrade path as usage grows

## 🏗️ Architecture

```
Frontend (React)
  ↓
Backend API (FastAPI)
  ├─ Search (Azure Cognitive Search)
  ├─ LLM (Azure OpenAI)
  └─ Storage (Azure Blob)
```

**Tech Stack**:
- Frontend: React 18 + TypeScript
- Backend: Python FastAPI
- LLM: Azure OpenAI (gpt-3.5-turbo)
- Search: Azure Cognitive Search
- Storage: Azure Blob Storage
- Hosting: Azure Static Web Apps + App Service
- CI/CD: GitHub Actions

## 📂 Project Structure

```
Team-2/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── main.py            # FastAPI app
│   │   ├── config.py          # Azure config
│   │   ├── models.py          # Request/response schemas
│   │   ├── services/          # Business logic
│   │   └── routes/            # API endpoints
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                   # React TypeScript app
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API client
│   │   └── styles/            # CSS
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── deployment/                 # Deployment scripts
│   ├── azure-setup.sh
│   └── github-actions.yml
│
├── docs/                       # Documentation
│   ├── API.md                 # API reference
│   ├── DEPLOYMENT.md          # Deployment guide
│   ├── RAG_DESIGN.md          # RAG architecture
│   └── TROUBLESHOOTING.md
│
└── .github/workflows/          # CI/CD
    └── deploy.yml
```

## 🚀 Deployment

### Local Development

**Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with Azure credentials
uvicorn src.main:app --reload
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Production (Azure)

See **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for complete instructions.

**TL;DR**:
1. Create Azure resources
2. Add GitHub Secrets
3. Push to `main` branch
4. GitHub Actions handles deployment

## 📖 Documentation

- **[API Reference](docs/API.md)** - Endpoint specs, configuration
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Azure setup, GitHub config
- **[RAG Design](docs/RAG_DESIGN.md)** - Architecture, chunking strategy
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues & fixes

## 💰 Cost Estimates

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| Cognitive Search | Free | $0 |
| App Service | B1 | $12 |
| Static Web Apps | Free | $0 |
| Blob Storage | Hot | $1-2 |
| Azure OpenAI | Pay-per-token | $5-20 |
| **Total** | | **$18-35** |

Based on <100 users/month, ~500 queries.

## 📊 Usage

### Chat Interface
1. Open the web application
2. Type a question about Bona products
3. Get instant answer with source documents
4. Click sources to see which TDS sheets were referenced

### Example Queries
- "What is the drying time for Bona Classic?"
- "How do I apply Bona Wave2K?"
- "What is VOC content of Bona TrafficHD?"
- "Differences between Bona finishes?"

## 🧪 Testing

### Backend Tests
```bash
cd backend
pip install pytest pytest-cov
pytest tests/ -v --cov=src
```

### API Health Check
```bash
curl https://api-endpoint/api/health
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🔐 Security

- No user authentication (public chatbot)
- No chat history persistence
- All API calls to Azure are authenticated
- Rate limiting recommended for production

## 🛠️ Maintenance

### Update Product Docs
1. Upload new TDS files to `ragf/` folder
2. Commit to `main` branch
3. Run document indexing script
4. New queries will use updated docs

### Monitor Costs
```bash
# Check Azure spend
az cost management query create --definition '{...}'
```

### Scale Up (when needed)
- Cognitive Search: Free → Standard ($15/month)
- App Service: B1 → B2 ($48/month)
- See docs/DEPLOYMENT.md for scaling guide

## 🎓 Learning Resources

- [Azure OpenAI Quickstart](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/quickstart)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React TypeScript Guide](https://react.dev/learn/typescript)
- [RAG Pattern Explained](https://python.langchain.com/docs/use_cases/question_answering/)

## 🐛 Troubleshooting

Common issues & solutions:
- **API returns 503**: RAG service not initialized → check Azure credentials
- **No documents retrieved**: Index empty → re-run document indexing
- **Slow responses**: High latency → check Azure OpenAI quota
- **Frontend not loading**: Static Web Apps not deployed → check CI/CD logs

See **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** for more.

## 📝 License

[Your License Here]

## 👥 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m "Add feature"`
3. Push to branch: `git push origin feature/your-feature`
4. Open Pull Request

## 📧 Support

For questions or issues:
1. Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Review [API.md](docs/API.md) for endpoint details
3. Create GitHub issue with error logs

## 🎉 Next Steps

- [ ] Deploy to Azure
- [ ] Test with real product queries
- [ ] Monitor costs and performance
- [ ] Gather user feedback
- [ ] Plan Phase 2: Chat history + authentication

---

**Status**: MVP Ready for Deployment ✅

**Last Updated**: August 26, 2024
