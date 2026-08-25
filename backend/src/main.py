import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.routes import chat
from src.services import RAGService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Global RAG service
rag_service_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global rag_service_instance
    
    # Startup
    logger.info(f"Starting Bona RAG API (environment: {settings.ENVIRONMENT})")
    try:
        rag_service_instance = RAGService()
        logger.info("RAG Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG Service: {e}")
        # Continue anyway - service will fail gracefully when used
    
    yield
    
    # Shutdown
    logger.info("Shutting down Bona RAG API")


# Create FastAPI app
app = FastAPI(
    title="Bona RAG API",
    description="RAG-powered support assistant for Bona flooring products",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (public chatbot)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(chat.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Bona RAG API",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "rag_service_ready": rag_service_instance is not None,
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )
