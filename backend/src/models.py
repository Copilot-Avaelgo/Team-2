from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    """Request schema for /chat endpoint"""
    query: str
    session_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the drying time for Bona Classic?",
                "session_id": "optional-session-id"
            }
        }


class RetrievedDocument(BaseModel):
    """Schema for retrieved documents from Cognitive Search"""
    content: str
    source: str
    score: float


class ChatResponse(BaseModel):
    """Response schema for /chat endpoint"""
    answer: str
    source_documents: List[RetrievedDocument]
    session_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Bona Classic has a drying time of 6-8 hours...",
                "source_documents": [
                    {
                        "content": "Product: Bona Classic...",
                        "source": "Bona_Classic_TDS_AU.txt",
                        "score": 0.95
                    }
                ],
                "session_id": "optional-session-id"
            }
        }
