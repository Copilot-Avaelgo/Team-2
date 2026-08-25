"""Tests for LLM service."""

import pytest
from unittest.mock import patch, MagicMock, call
from src.services.llm_service import LLMService
from src.models import RetrievedDocument


class TestLLMServiceInitialization:
    """Test LLMService initialization."""
    
    @patch("src.services.llm_service.AzureOpenAI")
    @patch("src.services.llm_service.settings")
    def test_init_success(self, mock_settings, mock_azure_openai_class):
        """Test successful initialization."""
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
        
        mock_client = MagicMock()
        mock_azure_openai_class.return_value = mock_client
        
        service = LLMService()
        
        assert service.client is not None
        assert service.deployment_name == "gpt-35-turbo"
        mock_azure_openai_class.assert_called_once()
    
    @patch("src.services.llm_service.AzureOpenAI")
    @patch("src.services.llm_service.settings")
    def test_init_failure(self, mock_settings, mock_azure_openai_class):
        """Test initialization failure handling."""
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
        
        mock_azure_openai_class.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception):
            LLMService()


class TestGenerateResponse:
    """Test generate_response method."""
    
    @patch("src.services.llm_service.AzureOpenAI")
    @patch("src.services.llm_service.settings")
    def test_generate_response_success(self, mock_settings, mock_azure_openai_class, sample_retrieved_documents):
        """Test successful response generation."""
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
        
        mock_client = MagicMock()
        mock_azure_openai_class.return_value = mock_client
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Bona Classic has a drying time of 6-8 hours."
        mock_client.chat.completions.create.return_value = mock_response
        
        service = LLMService()
        result = service.generate_response(
            "What is the drying time for Bona Classic?",
            sample_retrieved_documents
        )
        
        assert result == "Bona Classic has a drying time of 6-8 hours."
        mock_client.chat.completions.create.assert_called_once()
    
    @patch("src.services.llm_service.AzureOpenAI")
    @patch("src.services.llm_service.settings")
    def test_generate_response_with_empty_context(self, mock_settings, mock_azure_openai_class):
        """Test response generation with empty context."""
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
        
        mock_client = MagicMock()
        mock_azure_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "I don't have relevant documentation."
        mock_client.chat.completions.create.return_value = mock_response
        
        service = LLMService()
        result = service.generate_response("query", [])
        
        assert len(result) > 0
        mock_client.chat.completions.create.assert_called_once()
    
    @patch("src.services.llm_service.AzureOpenAI")
    @patch("src.services.llm_service.settings")
    def test_generate_response_with_custom_max_tokens(self, mock_settings, mock_azure_openai_class, sample_retrieved_documents):
        """Test response generation with custom max_tokens."""
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
        
        mock_client = MagicMock()
        mock_azure_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create.return_value = mock_response
        
        service = LLMService()
        service.generate_response("query", sample_retrieved_documents, max_tokens=256)
        
        # Verify max_tokens was passed correctly
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["max_tokens"] == 256
    
    @patch("src.services.llm_service.AzureOpenAI")
    @patch("src.services.llm_service.settings")
    def test_generate_response_exception(self, mock_settings, mock_azure_openai_class, sample_retrieved_documents):
        """Test response generation exception handling."""
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
        
        mock_client = MagicMock()
        mock_azure_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API error")
        
        service = LLMService()
        
        with pytest.raises(Exception):
            service.generate_response("query", sample_retrieved_documents)


class TestBuildContext:
    """Test _build_context method."""
    
    @patch("src.services.llm_service.AzureOpenAI")
    @patch("src.services.llm_service.settings")
    def test_build_context_with_documents(self, mock_settings, mock_azure_openai_class, sample_retrieved_documents):
        """Test building context from documents."""
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
        
        mock_client = MagicMock()
        mock_azure_openai_class.return_value = mock_client
        
        service = LLMService()
        context = service._build_context(sample_retrieved_documents)
        
        assert len(context) > 0
        assert "Bona Classic" in context
        assert "Bona_Classic_TDS.txt" in context
    
    @patch("src.services.llm_service.AzureOpenAI")
    @patch("src.services.llm_service.settings")
    def test_build_context_empty_documents(self, mock_settings, mock_azure_openai_class):
        """Test building context with no documents."""
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
        
        mock_client = MagicMock()
        mock_azure_openai_class.return_value = mock_client
        
        service = LLMService()
        context = service._build_context([])
        
        assert "No relevant product documentation found" in context
    
    @patch("src.services.llm_service.AzureOpenAI")
    @patch("src.services.llm_service.settings")
    def test_build_context_single_document(self, mock_settings, mock_azure_openai_class):
        """Test building context with single document."""
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
        
        mock_client = MagicMock()
        mock_azure_openai_class.return_value = mock_client
        
        documents = [
            RetrievedDocument(
                content="Single document content",
                source="single.txt",
                score=0.95
            )
        ]
        
        service = LLMService()
        context = service._build_context(documents)
        
        assert "Single document content" in context
        assert "single.txt" in context


class TestCreatePrompt:
    """Test _create_prompt method."""
    
    @patch("src.services.llm_service.AzureOpenAI")
    @patch("src.services.llm_service.settings")
    def test_create_prompt_structure(self, mock_settings, mock_azure_openai_class):
        """Test that prompt has correct structure."""
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
        
        mock_client = MagicMock()
        mock_azure_openai_class.return_value = mock_client
        
        service = LLMService()
        prompt = service._create_prompt("What is X?", "Context about X")
        
        assert "What is X?" in prompt
        assert "Context about X" in prompt
        assert "DOCUMENTATION:" in prompt or "Documentation" in prompt
    
    @patch("src.services.llm_service.AzureOpenAI")
    @patch("src.services.llm_service.settings")
    def test_create_prompt_with_special_characters(self, mock_settings, mock_azure_openai_class):
        """Test prompt creation with special characters."""
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
        
        mock_client = MagicMock()
        mock_azure_openai_class.return_value = mock_client
        
        service = LLMService()
        prompt = service._create_prompt(
            "What's @#$% about this?",
            "Context with special chars: @#$%"
        )
        
        assert len(prompt) > 0


class TestSystemMessage:
    """Test system message configuration."""
    
    @patch("src.services.llm_service.AzureOpenAI")
    @patch("src.services.llm_service.settings")
    def test_system_message_content(self, mock_settings, mock_azure_openai_class, sample_retrieved_documents):
        """Test that system message is correctly configured."""
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
        
        mock_client = MagicMock()
        mock_azure_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create.return_value = mock_response
        
        service = LLMService()
        service.generate_response("query", sample_retrieved_documents)
        
        # Check that system message was passed
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        
        assert len(messages) >= 1
        assert messages[0]["role"] == "system"
        assert "Bona" in messages[0]["content"]


class TestRequestParameters:
    """Test request parameter handling."""
    
    @patch("src.services.llm_service.AzureOpenAI")
    @patch("src.services.llm_service.settings")
    def test_request_parameters(self, mock_settings, mock_azure_openai_class, sample_retrieved_documents):
        """Test that all required parameters are passed."""
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
        
        mock_client = MagicMock()
        mock_azure_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create.return_value = mock_response
        
        service = LLMService()
        service.generate_response("query", sample_retrieved_documents)
        
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        
        assert "model" in call_kwargs
        assert "messages" in call_kwargs
        assert "temperature" in call_kwargs
        assert "max_tokens" in call_kwargs
        assert "top_p" in call_kwargs
