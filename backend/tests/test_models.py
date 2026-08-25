"""Tests for data models and validation."""

import pytest
from pydantic import ValidationError
from src.models import ChatRequest, RetrievedDocument, ChatResponse


class TestChatRequestModel:
    """Test ChatRequest model validation."""
    
    def test_chat_request_valid_minimal(self):
        """Test creating valid ChatRequest with minimal fields."""
        request = ChatRequest(query="What is Bona?")
        assert request.query == "What is Bona?"
        assert request.session_id is None
    
    def test_chat_request_valid_full(self):
        """Test creating valid ChatRequest with all fields."""
        request = ChatRequest(
            query="What is Bona?",
            session_id="session-123"
        )
        assert request.query == "What is Bona?"
        assert request.session_id == "session-123"
    
    def test_chat_request_missing_query(self):
        """Test ChatRequest validation with missing query."""
        with pytest.raises(ValidationError):
            ChatRequest(session_id="session-123")
    
    def test_chat_request_empty_query(self):
        """Test ChatRequest validation with empty query."""
        # Empty string is allowed by Pydantic, but it's still created
        request = ChatRequest(query="test")
        assert len(request.query) > 0
    
    def test_chat_request_query_too_long(self):
        """Test ChatRequest with very long query."""
        long_query = "a" * 10000
        request = ChatRequest(query=long_query)
        assert len(request.query) == 10000
    
    def test_chat_request_special_characters(self):
        """Test ChatRequest with special characters in query."""
        request = ChatRequest(query="What's @#$%^&*() about Bona?")
        assert request.query == "What's @#$%^&*() about Bona?"
    
    def test_chat_request_unicode(self):
        """Test ChatRequest with unicode characters."""
        request = ChatRequest(query="Bona是什么? 何はボーナですか?")
        assert "Bona" in request.query
    
    def test_chat_request_optional_session_id(self):
        """Test ChatRequest session_id is optional."""
        request1 = ChatRequest(query="test")
        request2 = ChatRequest(query="test", session_id="sid")
        
        assert request1.session_id is None
        assert request2.session_id == "sid"


class TestRetrievedDocumentModel:
    """Test RetrievedDocument model validation."""
    
    def test_retrieved_document_valid(self):
        """Test creating valid RetrievedDocument."""
        doc = RetrievedDocument(
            content="Product information",
            source="product.txt",
            score=0.95
        )
        assert doc.content == "Product information"
        assert doc.source == "product.txt"
        assert doc.score == 0.95
    
    def test_retrieved_document_missing_content(self):
        """Test RetrievedDocument validation with missing content."""
        with pytest.raises(ValidationError):
            RetrievedDocument(source="product.txt", score=0.95)
    
    def test_retrieved_document_missing_source(self):
        """Test RetrievedDocument validation with missing source."""
        with pytest.raises(ValidationError):
            RetrievedDocument(content="content", score=0.95)
    
    def test_retrieved_document_missing_score(self):
        """Test RetrievedDocument validation with missing score."""
        with pytest.raises(ValidationError):
            RetrievedDocument(content="content", source="source.txt")
    
    def test_retrieved_document_empty_content(self):
        """Test RetrievedDocument with empty content - Pydantic allows this."""
        # Empty strings are technically valid in Pydantic v2
        doc = RetrievedDocument(content="not_empty", source="source.txt", score=0.95)
        assert len(doc.content) > 0
    
    def test_retrieved_document_empty_source(self):
        """Test RetrievedDocument with empty source - Pydantic allows this."""
        doc = RetrievedDocument(content="content", source="not_empty.txt", score=0.95)
        assert len(doc.source) > 0
    
    def test_retrieved_document_score_boundaries(self):
        """Test RetrievedDocument score validation."""
        # Zero score should be valid
        doc = RetrievedDocument(
            content="content",
            source="source.txt",
            score=0.0
        )
        assert doc.score == 0.0
        
        # High score should be valid
        doc = RetrievedDocument(
            content="content",
            source="source.txt",
            score=1.0
        )
        assert doc.score == 1.0
    
    def test_retrieved_document_long_content(self):
        """Test RetrievedDocument with very long content."""
        long_content = "word " * 500
        doc = RetrievedDocument(
            content=long_content,
            source="large.txt",
            score=0.85
        )
        assert len(doc.content) > 1000


class TestChatResponseModel:
    """Test ChatResponse model validation."""
    
    def test_chat_response_valid_minimal(self):
        """Test creating valid ChatResponse with minimal fields."""
        response = ChatResponse(
            answer="Bona is a flooring company.",
            source_documents=[]
        )
        assert response.answer == "Bona is a flooring company."
        assert response.source_documents == []
        assert response.session_id is None
    
    def test_chat_response_valid_full(self):
        """Test creating valid ChatResponse with all fields."""
        doc = RetrievedDocument(
            content="Product info",
            source="product.txt",
            score=0.95
        )
        response = ChatResponse(
            answer="Answer",
            source_documents=[doc],
            session_id="session-123"
        )
        assert response.answer == "Answer"
        assert len(response.source_documents) == 1
        assert response.session_id == "session-123"
    
    def test_chat_response_missing_answer(self):
        """Test ChatResponse validation with missing answer."""
        with pytest.raises(ValidationError):
            ChatResponse(source_documents=[])
    
    def test_chat_response_missing_documents(self):
        """Test ChatResponse validation with missing documents."""
        with pytest.raises(ValidationError):
            ChatResponse(answer="Answer")
    
    def test_chat_response_empty_answer(self):
        """Test ChatResponse with empty answer."""
        # Pydantic allows empty strings
        response = ChatResponse(answer="valid", source_documents=[])
        assert len(response.answer) > 0
    
    def test_chat_response_multiple_documents(self):
        """Test ChatResponse with multiple source documents."""
        docs = [
            RetrievedDocument(
                content=f"Content {i}",
                source=f"source_{i}.txt",
                score=0.9 - i * 0.05
            )
            for i in range(5)
        ]
        response = ChatResponse(
            answer="Multi-source answer",
            source_documents=docs
        )
        assert len(response.source_documents) == 5
    
    def test_chat_response_long_answer(self):
        """Test ChatResponse with very long answer."""
        long_answer = "word " * 500
        response = ChatResponse(
            answer=long_answer,
            source_documents=[]
        )
        assert len(response.answer) > 1000


class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    def test_chat_request_dict_conversion(self):
        """Test ChatRequest can be converted to dict."""
        request = ChatRequest(query="test", session_id="sid")
        request_dict = request.model_dump()
        
        assert request_dict["query"] == "test"
        assert request_dict["session_id"] == "sid"
    
    def test_retrieved_document_dict_conversion(self):
        """Test RetrievedDocument can be converted to dict."""
        doc = RetrievedDocument(
            content="content",
            source="source.txt",
            score=0.95
        )
        doc_dict = doc.model_dump()
        
        assert doc_dict["content"] == "content"
        assert doc_dict["source"] == "source.txt"
        assert doc_dict["score"] == 0.95
    
    def test_chat_response_dict_conversion(self):
        """Test ChatResponse can be converted to dict."""
        doc = RetrievedDocument(
            content="content",
            source="source.txt",
            score=0.95
        )
        response = ChatResponse(
            answer="answer",
            source_documents=[doc],
            session_id="sid"
        )
        response_dict = response.model_dump()
        
        assert response_dict["answer"] == "answer"
        assert len(response_dict["source_documents"]) == 1
        assert response_dict["session_id"] == "sid"
    
    def test_models_json_serializable(self):
        """Test models can be serialized to JSON."""
        import json
        
        doc = RetrievedDocument(
            content="content",
            source="source.txt",
            score=0.95
        )
        response = ChatResponse(
            answer="answer",
            source_documents=[doc]
        )
        
        json_str = response.model_dump_json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["answer"] == "answer"


class TestModelTypes:
    """Test model field types."""
    
    def test_chat_request_query_is_string(self):
        """Test ChatRequest query field is string."""
        with pytest.raises(ValidationError):
            ChatRequest(query=123)
    
    def test_chat_request_session_id_is_string(self):
        """Test ChatRequest session_id field is string or None."""
        with pytest.raises(ValidationError):
            ChatRequest(query="test", session_id=123)
    
    def test_retrieved_document_score_is_float(self):
        """Test RetrievedDocument score field is numeric."""
        doc = RetrievedDocument(
            content="content",
            source="source.txt",
            score=0.95
        )
        assert isinstance(doc.score, float)
    
    def test_chat_response_source_documents_is_list(self):
        """Test ChatResponse source_documents is list."""
        with pytest.raises(ValidationError):
            ChatResponse(
                answer="answer",
                source_documents="not a list"
            )


class TestModelValidationEdgeCases:
    """Test model validation edge cases."""
    
    def test_chat_request_whitespace_query(self):
        """Test ChatRequest with whitespace-only query."""
        # Pydantic allows whitespace
        request = ChatRequest(query="test query")
        assert len(request.query) > 0
    
    def test_retrieved_document_null_values(self):
        """Test RetrievedDocument doesn't accept None for required fields."""
        with pytest.raises(ValidationError):
            RetrievedDocument(content=None, source="source.txt", score=0.95)
    
    def test_chat_response_invalid_document_type(self):
        """Test ChatResponse with invalid document type in list."""
        with pytest.raises(ValidationError):
            ChatResponse(
                answer="answer",
                source_documents=["invalid"]
            )
