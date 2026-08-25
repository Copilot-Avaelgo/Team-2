"""Tests for search service."""

import pytest
from unittest.mock import patch, MagicMock, call
from src.services.search_service import SearchService
from src.models import RetrievedDocument


class TestSearchServiceInitialization:
    """Test SearchService initialization."""
    
    @patch("src.services.search_service.SearchClient")
    @patch("src.services.search_service.AzureKeyCredential")
    @patch("src.services.search_service.settings")
    def test_init_success(self, mock_settings, mock_credential, mock_search_client):
        """Test successful initialization."""
        mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-service"
        mock_settings.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_settings.AZURE_SEARCH_API_KEY = "test-key"
        
        service = SearchService()
        
        assert service.search_client is not None
        mock_search_client.assert_called_once()
    
    @patch("src.services.search_service.SearchClient")
    @patch("src.services.search_service.settings")
    def test_init_failure(self, mock_settings, mock_search_client):
        """Test initialization failure handling."""
        mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-service"
        mock_settings.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_settings.AZURE_SEARCH_API_KEY = "test-key"
        
        mock_search_client.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception):
            SearchService()


class TestSearchDocuments:
    """Test search_documents method."""
    
    @patch("src.services.search_service.SearchClient")
    @patch("src.services.search_service.AzureKeyCredential")
    @patch("src.services.search_service.settings")
    def test_search_documents_success(self, mock_settings, mock_credential, mock_search_client_class):
        """Test successful document search."""
        # Setup mocks
        mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-service"
        mock_settings.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_settings.AZURE_SEARCH_API_KEY = "test-key"
        
        mock_client = MagicMock()
        mock_search_client_class.return_value = mock_client
        
        # Mock search results
        mock_client.search.return_value = [
            {
                "content": "Bona Classic drying time",
                "source": "product_guide.txt",
                "@search.score": 0.95
            },
            {
                "content": "Bona Classic application",
                "source": "application_guide.txt",
                "@search.score": 0.87
            }
        ]
        
        service = SearchService()
        results = service.search_documents("drying time")
        
        assert len(results) == 2
        assert all(isinstance(r, RetrievedDocument) for r in results)
        assert results[0].score == 0.95
        assert results[1].score == 0.87
    
    @patch("src.services.search_service.SearchClient")
    @patch("src.services.search_service.AzureKeyCredential")
    @patch("src.services.search_service.settings")
    def test_search_documents_empty_results(self, mock_settings, mock_credential, mock_search_client_class):
        """Test search with no results."""
        mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-service"
        mock_settings.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_settings.AZURE_SEARCH_API_KEY = "test-key"
        
        mock_client = MagicMock()
        mock_search_client_class.return_value = mock_client
        mock_client.search.return_value = []
        
        service = SearchService()
        results = service.search_documents("nonexistent query")
        
        assert len(results) == 0
    
    @patch("src.services.search_service.SearchClient")
    @patch("src.services.search_service.AzureKeyCredential")
    @patch("src.services.search_service.settings")
    def test_search_documents_with_top_k(self, mock_settings, mock_credential, mock_search_client_class):
        """Test search with custom top_k parameter."""
        mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-service"
        mock_settings.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_settings.AZURE_SEARCH_API_KEY = "test-key"
        
        mock_client = MagicMock()
        mock_search_client_class.return_value = mock_client
        mock_client.search.return_value = []
        
        service = SearchService()
        service.search_documents("query", top_k=10)
        
        # Verify search was called with correct top parameter
        mock_client.search.assert_called_once()
        call_kwargs = mock_client.search.call_args[1]
        assert call_kwargs.get("top") == 10
    
    @patch("src.services.search_service.SearchClient")
    @patch("src.services.search_service.AzureKeyCredential")
    @patch("src.services.search_service.settings")
    def test_search_documents_missing_source(self, mock_settings, mock_credential, mock_search_client_class):
        """Test search result with missing source field."""
        mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-service"
        mock_settings.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_settings.AZURE_SEARCH_API_KEY = "test-key"
        
        mock_client = MagicMock()
        mock_search_client_class.return_value = mock_client
        
        # Result without 'source' field
        mock_client.search.return_value = [
            {
                "content": "Bona Classic drying time",
                "@search.score": 0.95
            }
        ]
        
        service = SearchService()
        results = service.search_documents("query")
        
        assert len(results) == 1
        assert results[0].source == "unknown"
    
    @patch("src.services.search_service.SearchClient")
    @patch("src.services.search_service.AzureKeyCredential")
    @patch("src.services.search_service.settings")
    def test_search_documents_exception(self, mock_settings, mock_credential, mock_search_client_class):
        """Test search exception handling."""
        mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-service"
        mock_settings.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_settings.AZURE_SEARCH_API_KEY = "test-key"
        
        mock_client = MagicMock()
        mock_search_client_class.return_value = mock_client
        mock_client.search.side_effect = Exception("Search failed")
        
        service = SearchService()
        
        with pytest.raises(Exception):
            service.search_documents("query")


class TestIndexDocuments:
    """Test index_documents method."""
    
    @patch("src.services.search_service.SearchClient")
    @patch("src.services.search_service.AzureKeyCredential")
    @patch("src.services.search_service.settings")
    def test_index_documents_success(self, mock_settings, mock_credential, mock_search_client_class, sample_documents):
        """Test successful document indexing."""
        mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-service"
        mock_settings.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_settings.AZURE_SEARCH_API_KEY = "test-key"
        
        mock_client = MagicMock()
        mock_search_client_class.return_value = mock_client
        mock_client.upload_documents.return_value = True
        
        service = SearchService()
        result = service.index_documents(sample_documents)
        
        assert result is True
        mock_client.upload_documents.assert_called_once_with(documents=sample_documents)
    
    @patch("src.services.search_service.SearchClient")
    @patch("src.services.search_service.AzureKeyCredential")
    @patch("src.services.search_service.settings")
    def test_index_documents_empty_list(self, mock_settings, mock_credential, mock_search_client_class):
        """Test indexing empty document list."""
        mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-service"
        mock_settings.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_settings.AZURE_SEARCH_API_KEY = "test-key"
        
        mock_client = MagicMock()
        mock_search_client_class.return_value = mock_client
        mock_client.upload_documents.return_value = True
        
        service = SearchService()
        result = service.index_documents([])
        
        assert result is True
        mock_client.upload_documents.assert_called_once_with(documents=[])
    
    @patch("src.services.search_service.SearchClient")
    @patch("src.services.search_service.AzureKeyCredential")
    @patch("src.services.search_service.settings")
    def test_index_documents_exception(self, mock_settings, mock_credential, mock_search_client_class, sample_documents):
        """Test indexing exception handling."""
        mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-service"
        mock_settings.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_settings.AZURE_SEARCH_API_KEY = "test-key"
        
        mock_client = MagicMock()
        mock_search_client_class.return_value = mock_client
        mock_client.upload_documents.side_effect = Exception("Upload failed")
        
        service = SearchService()
        
        with pytest.raises(Exception):
            service.index_documents(sample_documents)
    
    @patch("src.services.search_service.SearchClient")
    @patch("src.services.search_service.AzureKeyCredential")
    @patch("src.services.search_service.settings")
    def test_index_documents_large_batch(self, mock_settings, mock_credential, mock_search_client_class):
        """Test indexing large batch of documents."""
        mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-service"
        mock_settings.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_settings.AZURE_SEARCH_API_KEY = "test-key"
        
        mock_client = MagicMock()
        mock_search_client_class.return_value = mock_client
        mock_client.upload_documents.return_value = True
        
        # Create large batch
        large_batch = [
            {
                "id": f"doc_{i}",
                "content": f"Document content {i}",
                "source": f"source_{i % 5}.txt"
            }
            for i in range(100)
        ]
        
        service = SearchService()
        result = service.index_documents(large_batch)
        
        assert result is True


class TestDocumentStructure:
    """Test RetrievedDocument structure."""
    
    @patch("src.services.search_service.SearchClient")
    @patch("src.services.search_service.AzureKeyCredential")
    @patch("src.services.search_service.settings")
    def test_retrieved_document_structure(self, mock_settings, mock_credential, mock_search_client_class):
        """Test RetrievedDocument has correct structure."""
        mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-service"
        mock_settings.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_settings.AZURE_SEARCH_API_KEY = "test-key"
        
        mock_client = MagicMock()
        mock_search_client_class.return_value = mock_client
        mock_client.search.return_value = [
            {
                "content": "Test content",
                "source": "test.txt",
                "@search.score": 0.99
            }
        ]
        
        service = SearchService()
        results = service.search_documents("query")
        
        doc = results[0]
        assert hasattr(doc, "content")
        assert hasattr(doc, "source")
        assert hasattr(doc, "score")
        assert doc.content == "Test content"
        assert doc.source == "test.txt"
        assert doc.score == 0.99


class TestSearchQueryProcessing:
    """Test search query processing."""
    
    @patch("src.services.search_service.SearchClient")
    @patch("src.services.search_service.AzureKeyCredential")
    @patch("src.services.search_service.settings")
    def test_search_with_special_characters(self, mock_settings, mock_credential, mock_search_client_class):
        """Test search with special characters in query."""
        mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-service"
        mock_settings.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_settings.AZURE_SEARCH_API_KEY = "test-key"
        
        mock_client = MagicMock()
        mock_search_client_class.return_value = mock_client
        mock_client.search.return_value = []
        
        service = SearchService()
        service.search_documents("query with @#$% special chars & symbols")
        
        mock_client.search.assert_called_once()
    
    @patch("src.services.search_service.SearchClient")
    @patch("src.services.search_service.AzureKeyCredential")
    @patch("src.services.search_service.settings")
    def test_search_with_long_query(self, mock_settings, mock_credential, mock_search_client_class):
        """Test search with very long query."""
        mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-service"
        mock_settings.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_settings.AZURE_SEARCH_API_KEY = "test-key"
        
        mock_client = MagicMock()
        mock_search_client_class.return_value = mock_client
        mock_client.search.return_value = []
        
        long_query = " ".join(["word"] * 100)
        
        service = SearchService()
        service.search_documents(long_query)
        
        mock_client.search.assert_called_once()
