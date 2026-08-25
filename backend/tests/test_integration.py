"""Additional comprehensive tests for RAG Service and integration."""

import pytest
from unittest.mock import patch, MagicMock, call
from src.services import RAGService
from src.models import RetrievedDocument, ChatResponse
from src.services.document_processor import DocumentProcessor


class TestRAGServiceInitialization:
    """Test RAGService initialization."""
    
    @patch("src.services.SearchService")
    @patch("src.services.LLMService")
    @patch("src.services.DocumentProcessor")
    def test_rag_service_init_success(self, mock_doc_proc, mock_llm, mock_search):
        """Test successful RAG Service initialization."""
        service = RAGService()
        
        assert service.search_service is not None
        assert service.llm_service is not None
        assert service.doc_processor is not None
    
    @patch("src.services.SearchService")
    @patch("src.services.LLMService")
    @patch("src.services.DocumentProcessor")
    def test_rag_service_init_failure(self, mock_doc_proc, mock_llm, mock_search):
        """Test RAG Service initialization failure."""
        mock_search.side_effect = Exception("Search service failed")
        
        with pytest.raises(Exception):
            RAGService()


class TestProcessQuery:
    """Test process_query method."""
    
    @patch("src.services.SearchService")
    @patch("src.services.LLMService")
    @patch("src.services.DocumentProcessor")
    def test_process_query_success(self, mock_doc_proc, mock_llm, mock_search, sample_retrieved_documents):
        """Test successful query processing."""
        # Setup mocks
        mock_search_instance = MagicMock()
        mock_search_instance.search_documents.return_value = sample_retrieved_documents
        mock_search.return_value = mock_search_instance
        
        mock_llm_instance = MagicMock()
        mock_llm_instance.generate_response.return_value = "Bona Classic drying time is 6-8 hours."
        mock_llm.return_value = mock_llm_instance
        
        service = RAGService()
        response = service.process_query("What is the drying time?")
        
        assert isinstance(response, ChatResponse)
        assert len(response.answer) > 0
        assert len(response.source_documents) == len(sample_retrieved_documents)
    
    @patch("src.services.SearchService")
    @patch("src.services.LLMService")
    @patch("src.services.DocumentProcessor")
    def test_process_query_no_documents_found(self, mock_doc_proc, mock_llm, mock_search):
        """Test query processing when no documents are found."""
        mock_search_instance = MagicMock()
        mock_search_instance.search_documents.return_value = []
        mock_search.return_value = mock_search_instance
        
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        
        service = RAGService()
        response = service.process_query("query")
        
        assert isinstance(response, ChatResponse)
        assert len(response.source_documents) == 0
        assert "couldn't find" in response.answer.lower()
    
    @patch("src.services.SearchService")
    @patch("src.services.LLMService")
    @patch("src.services.DocumentProcessor")
    def test_process_query_with_session_id(self, mock_doc_proc, mock_llm, mock_search, sample_retrieved_documents):
        """Test query processing with session ID."""
        mock_search_instance = MagicMock()
        mock_search_instance.search_documents.return_value = sample_retrieved_documents
        mock_search.return_value = mock_search_instance
        
        mock_llm_instance = MagicMock()
        mock_llm_instance.generate_response.return_value = "Answer"
        mock_llm.return_value = mock_llm_instance
        
        service = RAGService()
        response = service.process_query("query", session_id="test-session-123")
        
        assert response.session_id == "test-session-123"
    
    @patch("src.services.SearchService")
    @patch("src.services.LLMService")
    @patch("src.services.DocumentProcessor")
    def test_process_query_exception(self, mock_doc_proc, mock_llm, mock_search):
        """Test query processing exception handling."""
        mock_search_instance = MagicMock()
        mock_search_instance.search_documents.side_effect = Exception("Search failed")
        mock_search.return_value = mock_search_instance
        
        service = RAGService()
        
        with pytest.raises(Exception):
            service.process_query("query")


class TestInitializeKnowledgeBase:
    """Test initialize_knowledge_base method."""
    
    @patch("src.services.SearchService")
    @patch("src.services.LLMService")
    @patch("src.services.DocumentProcessor")
    def test_initialize_knowledge_base_success(self, mock_doc_proc, mock_llm, mock_search, sample_documents, temp_documents_folder):
        """Test successful knowledge base initialization."""
        mock_search_instance = MagicMock()
        mock_search_instance.index_documents.return_value = True
        mock_search.return_value = mock_search_instance
        
        mock_doc_proc_instance = MagicMock()
        mock_doc_proc_instance.load_and_process.return_value = sample_documents
        mock_doc_proc.return_value = mock_doc_proc_instance
        
        service = RAGService()
        result = service.initialize_knowledge_base(str(temp_documents_folder))
        
        assert result is True
        mock_doc_proc_instance.load_and_process.assert_called_once()
        mock_search_instance.index_documents.assert_called_once()
    
    @patch("src.services.SearchService")
    @patch("src.services.LLMService")
    @patch("src.services.DocumentProcessor")
    def test_initialize_knowledge_base_no_documents(self, mock_doc_proc, mock_llm, mock_search):
        """Test knowledge base initialization with no documents."""
        mock_search_instance = MagicMock()
        mock_search.return_value = mock_search_instance
        
        mock_doc_proc_instance = MagicMock()
        mock_doc_proc_instance.load_and_process.return_value = []
        mock_doc_proc.return_value = mock_doc_proc_instance
        
        service = RAGService()
        result = service.initialize_knowledge_base("/some/path")
        
        assert result is False
    
    @patch("src.services.SearchService")
    @patch("src.services.LLMService")
    @patch("src.services.DocumentProcessor")
    def test_initialize_knowledge_base_exception(self, mock_doc_proc, mock_llm, mock_search):
        """Test knowledge base initialization exception handling."""
        mock_search_instance = MagicMock()
        mock_search.return_value = mock_search_instance
        
        mock_doc_proc_instance = MagicMock()
        mock_doc_proc_instance.load_and_process.side_effect = Exception("Load failed")
        mock_doc_proc.return_value = mock_doc_proc_instance
        
        service = RAGService()
        
        with pytest.raises(Exception):
            service.initialize_knowledge_base("/some/path")


class TestDocumentProcessorIntegration:
    """Test DocumentProcessor integration with RAG Service."""
    
    def test_processor_chunking_workflow(self, temp_documents_folder):
        """Test complete chunking workflow."""
        processor = DocumentProcessor(chunk_size=100, overlap=20)
        
        # Process folder
        documents = processor.load_and_process(str(temp_documents_folder))
        
        # Verify results
        assert len(documents) > 0
        assert all("id" in doc for doc in documents)
        assert all("content" in doc for doc in documents)
        assert all("source" in doc for doc in documents)
    
    def test_processor_handles_large_files(self):
        """Test processor handles large files."""
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a large file
            large_file = os.path.join(tmpdir, "large.txt")
            with open(large_file, 'w') as f:
                for i in range(1000):
                    f.write(f"This is line {i} with some content. " * 10 + "\n")
            
            processor = DocumentProcessor(chunk_size=100, overlap=20)
            documents = processor.load_and_process(tmpdir)
            
            assert len(documents) > 0


class TestSearchServiceIntegration:
    """Test SearchService integration."""
    
    @patch("src.services.search_service.SearchClient")
    @patch("src.services.search_service.AzureKeyCredential")
    @patch("src.services.search_service.settings")
    def test_index_and_search_workflow(self, mock_settings, mock_credential, mock_search_client_class, sample_documents, sample_retrieved_documents):
        """Test indexing and searching workflow."""
        from src.services.search_service import SearchService
        
        mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-service"
        mock_settings.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_settings.AZURE_SEARCH_API_KEY = "test-key"
        
        mock_client = MagicMock()
        mock_search_client_class.return_value = mock_client
        
        # Mock upload
        mock_client.upload_documents.return_value = True
        
        # Index documents
        service = SearchService()
        index_result = service.index_documents(sample_documents)
        assert index_result is True
        
        # Search for documents
        mock_client.search.return_value = [
            {"content": doc.content, "source": doc.source, "@search.score": doc.score}
            for doc in sample_retrieved_documents
        ]
        
        search_result = service.search_documents("test query")
        assert len(search_result) == len(sample_retrieved_documents)


class TestLLMServiceIntegration:
    """Test LLMService integration."""
    
    @patch("src.services.llm_service.AzureOpenAI")
    @patch("src.services.llm_service.settings")
    def test_context_and_prompt_building(self, mock_settings, mock_azure_openai_class, sample_retrieved_documents):
        """Test context and prompt building."""
        from src.services.llm_service import LLMService
        
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
        
        mock_client = MagicMock()
        mock_azure_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated response"
        mock_client.chat.completions.create.return_value = mock_response
        
        service = LLMService()
        
        # Test context building
        context = service._build_context(sample_retrieved_documents)
        assert len(context) > 0
        assert "Bona" in context
        
        # Test prompt creation
        prompt = service._create_prompt("test query", context)
        assert "test query" in prompt
        assert context in prompt
        
        # Test response generation
        response = service.generate_response("test query", sample_retrieved_documents)
        assert response == "Generated response"


class TestErrorHandlingAcrossServices:
    """Test error handling across services."""
    
    @patch("src.services.SearchService")
    @patch("src.services.LLMService")
    @patch("src.services.DocumentProcessor")
    def test_graceful_degradation_on_search_error(self, mock_doc_proc, mock_llm, mock_search):
        """Test graceful degradation when search fails."""
        mock_search_instance = MagicMock()
        mock_search_instance.search_documents.side_effect = Exception("Search service down")
        mock_search.return_value = mock_search_instance
        
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        
        service = RAGService()
        
        with pytest.raises(Exception):
            service.process_query("query")
    
    @patch("src.services.SearchService")
    @patch("src.services.LLMService")
    @patch("src.services.DocumentProcessor")
    def test_graceful_degradation_on_llm_error(self, mock_doc_proc, mock_llm, mock_search, sample_retrieved_documents):
        """Test graceful degradation when LLM fails."""
        mock_search_instance = MagicMock()
        mock_search_instance.search_documents.return_value = sample_retrieved_documents
        mock_search.return_value = mock_search_instance
        
        mock_llm_instance = MagicMock()
        mock_llm_instance.generate_response.side_effect = Exception("LLM service error")
        mock_llm.return_value = mock_llm_instance
        
        service = RAGService()
        
        with pytest.raises(Exception):
            service.process_query("query")


class TestPerformanceAndScaling:
    """Test performance and scaling aspects."""
    
    @patch("src.services.SearchService")
    @patch("src.services.LLMService")
    @patch("src.services.DocumentProcessor")
    def test_large_context_handling(self, mock_doc_proc, mock_llm, mock_search, large_document_set):
        """Test handling of large context."""
        mock_search_instance = MagicMock()
        mock_search_instance.search_documents.return_value = large_document_set
        mock_search.return_value = mock_search_instance
        
        mock_llm_instance = MagicMock()
        mock_llm_instance.generate_response.return_value = "Response based on large context"
        mock_llm.return_value = mock_llm_instance
        
        service = RAGService()
        response = service.process_query("query")
        
        assert len(response.source_documents) == len(large_document_set)
    
    @patch("src.services.SearchService")
    @patch("src.services.LLMService")
    @patch("src.services.DocumentProcessor")
    def test_batch_document_processing(self, mock_doc_proc, mock_llm, mock_search):
        """Test batch document processing."""
        # Create large batch of documents
        large_batch = [
            {
                "id": f"doc_{i}",
                "content": f"Document {i} content",
                "source": f"source_{i}.txt"
            }
            for i in range(100)
        ]
        
        mock_search_instance = MagicMock()
        mock_search_instance.index_documents.return_value = True
        mock_search.return_value = mock_search_instance
        
        mock_doc_proc_instance = MagicMock()
        mock_doc_proc_instance.load_and_process.return_value = large_batch
        mock_doc_proc.return_value = mock_doc_proc_instance
        
        service = RAGService()
        result = service.initialize_knowledge_base("/path")
        
        assert result is True
