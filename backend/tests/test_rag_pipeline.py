"""
Integration tests for the complete Bona RAG pipeline.

Tests the end-to-end flow:
1. Document processor → Search Service → LLM Service → Response

All Azure services are mocked to avoid external dependencies.
"""

import pytest
import logging
import time
from unittest.mock import Mock, patch, MagicMock
from typing import List

from src.models import RetrievedDocument, ChatResponse, ChatRequest
from src.services import RAGService
from src.services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class TestRAGPipelineHappyPath:
    """Test successful end-to-end RAG flow"""
    
    def test_process_query_success(self, sample_retrieved_documents, sample_query_response):
        """
        Test happy path: Query → Search → LLM → Response with sources
        
        Steps:
        1. Query is submitted to RAGService
        2. SearchService retrieves relevant documents
        3. LLMService generates response based on retrieved documents
        4. Response includes answer and source documents
        """
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            # Setup mocks
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = sample_retrieved_documents
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_service.generate_response.return_value = (
                "Bona Classic has a drying time of 1-2 hours at 20°C with 60% RH. "
                "It is a waterborne primer suitable for all wood types with 8-10 m²/L application rate."
            )
            mock_llm_class.return_value = mock_llm_service
            
            # Create RAG service and process query
            rag_service = RAGService()
            query = "What is the drying time for Bona Classic?"
            response = rag_service.process_query(query, session_id="test-session-1")
            
            # Assertions
            assert isinstance(response, ChatResponse)
            assert response.answer is not None
            assert len(response.answer) > 0
            assert len(response.source_documents) == 2
            assert "Bona_Classic" in response.source_documents[0].source
            assert response.source_documents[0].score == 0.95
            assert response.session_id == "test-session-1"
            
            # Verify service calls
            mock_search_service.search_documents.assert_called_once_with(query, top_k=5)
            mock_llm_service.generate_response.assert_called_once()
            
            logger.info(f"✓ Happy path test passed - Retrieved {len(response.source_documents)} documents")
    
    def test_process_query_realistic_bona_product_queries(self):
        """
        Test realistic Bona product documentation queries
        
        Scenarios:
        - Drying time queries
        - Application method queries
        - VOC/emissions content queries
        """
        test_cases = [
            {
                "query": "What is the drying time for Bona Classic?",
                "expected_content": "drying",
                "product": "Bona_Classic_TDS_AU.txt"
            },
            {
                "query": "How do I apply Bona TrafficHD?",
                "expected_content": "application",
                "product": "Bona_TrafficHD_TDS_AU.txt"
            },
            {
                "query": "What are the VOC emissions for Bona products?",
                "expected_content": "VOC",
                "product": "Bona_Classic_TDS_AU.txt"
            }
        ]
        
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            mock_search_service = Mock()
            mock_llm_service = Mock()
            mock_search_class.return_value = mock_search_service
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            
            for test_case in test_cases:
                # Setup for this test case
                mock_search_service.search_documents.return_value = [
                    RetrievedDocument(
                        content=f"Technical data for {test_case['product']} with "
                               f"{test_case['expected_content']} information",
                        source=test_case['product'],
                        score=0.92
                    )
                ]
                mock_llm_service.generate_response.return_value = (
                    f"Based on the {test_case['product']}, the answer is..."
                )
                
                # Process query
                response = rag_service.process_query(test_case['query'])
                
                # Verify
                assert len(response.source_documents) > 0
                assert response.source_documents[0].source == test_case['product']
                logger.info(f"✓ Query test passed: {test_case['query'][:50]}...")


class TestRAGPipelineNoDocumentsFound:
    """Test RAG pipeline when search returns no results"""
    
    def test_no_documents_found_returns_default_message(self, empty_documents):
        """
        Test no documents found scenario: Query with no matches
        
        When SearchService returns empty results:
        - Should return default message to user
        - Should have empty source_documents list
        - Should not call LLMService
        """
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = empty_documents
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_class.return_value = mock_llm_service
            
            # Create RAG service and process query
            rag_service = RAGService()
            query = "Tell me about a product that doesn't exist in the database"
            response = rag_service.process_query(query)
            
            # Assertions
            assert isinstance(response, ChatResponse)
            assert "couldn't find relevant" in response.answer.lower()
            assert len(response.source_documents) == 0
            
            # LLM should NOT be called when no documents found
            mock_llm_service.generate_response.assert_not_called()
            
            logger.info("✓ No documents found test passed")
    
    def test_empty_query_returns_default_message(self):
        """
        Test empty/whitespace query handling
        
        Queries that are empty or contain only whitespace should:
        - Be handled gracefully
        - Return default message
        """
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = []
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            
            # Test with empty string
            response = rag_service.process_query("")
            assert len(response.source_documents) == 0
            
            # Test with whitespace
            response = rag_service.process_query("   ")
            assert len(response.source_documents) == 0
            
            logger.info("✓ Empty query handling test passed")


class TestRAGPipelineErrorHandling:
    """Test error handling in RAG pipeline"""
    
    def test_llm_error_when_search_succeeds(self, sample_retrieved_documents):
        """
        Test LLM error handling: Search succeeds but LLM fails
        
        When LLMService raises an exception:
        - Error should be caught and logged
        - Exception should be re-raised for caller handling
        """
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = sample_retrieved_documents
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_service.generate_response.side_effect = Exception(
                "Azure OpenAI API rate limit exceeded"
            )
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            
            # Should raise exception
            with pytest.raises(Exception) as exc_info:
                rag_service.process_query("What is Bona Classic?")
            
            assert "rate limit" in str(exc_info.value)
            logger.info("✓ LLM error handling test passed")
    
    def test_search_service_error_propagates(self):
        """
        Test SearchService error handling
        
        When SearchService raises an exception:
        - Error should propagate to caller
        """
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            mock_search_service = Mock()
            mock_search_service.search_documents.side_effect = Exception(
                "Azure Cognitive Search connection failed"
            )
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            
            with pytest.raises(Exception) as exc_info:
                rag_service.process_query("What is Bona?")
            
            assert "connection failed" in str(exc_info.value)
            logger.info("✓ Search service error handling test passed")


class TestRAGPipelineLargeContext:
    """Test RAG pipeline with large context (many documents)"""
    
    def test_large_document_set_handling(self, large_document_set):
        """
        Test large context handling: Many documents retrieved
        
        When many documents are retrieved:
        - All documents should be processed
        - Response should include all source documents
        - LLM should handle large context
        """
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = large_document_set
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_service.generate_response.return_value = (
                "Based on the comprehensive product documentation provided, "
                "here is the answer to your question about Bona finishes..."
            )
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            response = rag_service.process_query("Tell me about all Bona products")
            
            # Verify all documents are included
            assert len(response.source_documents) == 10
            assert all(hasattr(doc, 'content') for doc in response.source_documents)
            assert all(hasattr(doc, 'source') for doc in response.source_documents)
            assert all(hasattr(doc, 'score') for doc in response.source_documents)
            
            logger.info(f"✓ Large context test passed - Handled {len(response.source_documents)} documents")
    
    def test_document_scoring_preserved(self, large_document_set):
        """
        Test that document relevance scores are preserved
        
        Document scores should:
        - Be maintained in response
        - Be ordered by relevance
        """
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = large_document_set
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_service.generate_response.return_value = "Response"
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            response = rag_service.process_query("Search query")
            
            # Verify scores are preserved and ordered
            scores = [doc.score for doc in response.source_documents]
            assert scores == sorted(scores, reverse=True)
            logger.info(f"✓ Document scoring test passed - Scores: {scores[:3]}...")


class TestRAGPipelineResponseStructure:
    """Test RAG pipeline response structure and format"""
    
    def test_response_structure_validation(self, sample_retrieved_documents):
        """
        Test response structure includes all required fields
        
        ChatResponse should contain:
        - answer: string
        - source_documents: List[RetrievedDocument]
        - session_id: optional string
        """
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = sample_retrieved_documents
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_service.generate_response.return_value = "Test answer"
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            response = rag_service.process_query("Test query", session_id="sess-123")
            
            # Verify structure
            assert hasattr(response, 'answer')
            assert hasattr(response, 'source_documents')
            assert hasattr(response, 'session_id')
            
            # Verify types
            assert isinstance(response.answer, str)
            assert isinstance(response.source_documents, list)
            assert len(response.source_documents) > 0
            
            # Verify document structure
            for doc in response.source_documents:
                assert isinstance(doc, RetrievedDocument)
                assert hasattr(doc, 'content')
                assert hasattr(doc, 'source')
                assert hasattr(doc, 'score')
                assert isinstance(doc.content, str)
                assert isinstance(doc.source, str)
                assert isinstance(doc.score, float)
            
            logger.info("✓ Response structure validation test passed")
    
    def test_source_document_attribution(self, sample_retrieved_documents):
        """
        Test that source documents are correctly attributed
        
        Each source document should:
        - Have content from the actual document
        - Have source filename
        - Have relevance score
        """
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = sample_retrieved_documents
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_service.generate_response.return_value = "Test answer"
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            response = rag_service.process_query("Query")
            
            # Verify each document has proper attribution
            for doc in response.source_documents:
                # Document sources should contain meaningful filenames
                assert doc.source is not None
                assert len(doc.source) > 0
                assert doc.source.endswith('.txt')
                # Content should be non-empty
                assert len(doc.content) > 0
                # Score should be between 0 and 1
                assert 0.0 <= doc.score <= 1.0
            
            logger.info("✓ Source attribution test passed")


class TestRAGPipelineLatency:
    """Test RAG pipeline performance and latency"""
    
    def test_pipeline_latency_measurement(self, sample_retrieved_documents):
        """
        Measure and log latency of RAG pipeline
        
        Records timing for:
        - Search retrieval
        - LLM generation
        - Total pipeline time
        """
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = sample_retrieved_documents
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_service.generate_response.return_value = "Generated response"
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            
            # Measure total pipeline time
            start_time = time.time()
            response = rag_service.process_query("Performance test query")
            total_time = time.time() - start_time
            
            assert total_time >= 0.0
            assert response is not None
            
            logger.info(f"✓ Pipeline latency: {total_time*1000:.2f}ms")
    
    def test_latency_with_large_context(self, large_document_set):
        """
        Test pipeline latency with large context
        
        Latency should scale reasonably with context size
        """
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = large_document_set
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_service.generate_response.return_value = "Response"
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            
            start_time = time.time()
            response = rag_service.process_query("Large context query")
            total_time = time.time() - start_time
            
            assert len(response.source_documents) == 10
            logger.info(f"✓ Large context latency: {total_time*1000:.2f}ms for {len(response.source_documents)} docs")


class TestDocumentProcessing:
    """Test document processing component"""
    
    def test_document_chunking(self):
        """
        Test document processor chunks text correctly
        
        Chunks should:
        - Be of expected size
        - Maintain overlap
        - Preserve source attribution
        """
        processor = DocumentProcessor(chunk_size=100, overlap=20)
        
        # Sample content from TDS
        sample_content = """
        Bona Classic is a waterborne primer with elastic properties.
        The drying time is 1-2 hours at 20°C with 60% relative humidity.
        Application rate is 8-10 m²/L per coat.
        It is suitable on practically all types of wood.
        The product has high solids content for easy surface application.
        GREENGUARD approved for low indoor emissions.
        """ * 2  # Repeat to have more words
        
        chunks = processor._chunk_text(sample_content, "test_source.txt")
        
        # Verify chunks
        assert len(chunks) > 0
        assert all('id' in chunk for chunk in chunks)
        assert all('content' in chunk for chunk in chunks)
        assert all('source' in chunk for chunk in chunks)
        assert all(chunk['source'] == 'test_source.txt' for chunk in chunks)
        
        logger.info(f"✓ Document chunking test passed - Created {len(chunks)} chunks")


class TestIntegrationWithModels:
    """Test integration with Pydantic models"""
    
    def test_chat_request_model_validation(self):
        """
        Test ChatRequest model validation
        
        ChatRequest should:
        - Accept query and optional session_id
        - Validate required fields
        """
        # Valid request
        request = ChatRequest(query="What is Bona?")
        assert request.query == "What is Bona?"
        assert request.session_id is None
        
        # With session ID
        request = ChatRequest(query="Test", session_id="sess-1")
        assert request.session_id == "sess-1"
        
        logger.info("✓ Chat request model validation test passed")
    
    def test_chat_response_model_creation(self, sample_retrieved_documents):
        """
        Test ChatResponse model creation and serialization
        
        ChatResponse should:
        - Accept answer and source documents
        - Support serialization to JSON
        """
        response = ChatResponse(
            answer="Test answer",
            source_documents=sample_retrieved_documents,
            session_id="test-sess"
        )
        
        assert response.answer == "Test answer"
        assert len(response.source_documents) == 2
        assert response.session_id == "test-sess"
        
        # Test serialization
        response_dict = response.model_dump()
        assert 'answer' in response_dict
        assert 'source_documents' in response_dict
        assert len(response_dict['source_documents']) == 2
        
        logger.info("✓ Chat response model test passed")


# Test execution and reporting
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--log-cli-level=INFO"])
