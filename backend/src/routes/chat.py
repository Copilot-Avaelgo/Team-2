import logging
from fastapi import APIRouter, HTTPException
from src.models import ChatRequest, ChatResponse
from src.services import RAGService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])

# Initialize RAG service (singleton)
try:
    rag_service = RAGService()
except Exception as e:
    logger.error(f"Failed to initialize RAG service at startup: {e}")
    rag_service = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process user query through RAG pipeline
    
    Args:
        request: ChatRequest with user query and optional session_id
        
    Returns:
        ChatResponse with answer and source documents
    """
    if not rag_service:
        raise HTTPException(
            status_code=503,
            detail="RAG service not initialized. Check server logs."
        )
    
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )
    
    try:
        response = rag_service.process_query(
            query=request.query.strip(),
            session_id=request.session_id
        )
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for deployment"""
    return {
        "status": "healthy",
        "rag_service_ready": rag_service is not None
    }
