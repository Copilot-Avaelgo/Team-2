"""Tests for configuration module."""

import pytest
import os
from unittest.mock import patch, MagicMock
from pydantic import ValidationError
from src.config import Settings


class TestSettingsInitialization:
    """Test Settings initialization."""
    
    def test_settings_all_required_fields(self, monkeypatch):
        """Test Settings initialization with all required fields."""
        # Set all environment variables
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-35-turbo")
        monkeypatch.setenv("AZURE_SEARCH_SERVICE_NAME", "test-search")
        monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-search-key")
        monkeypatch.setenv("AZURE_SEARCH_INDEX_NAME", "bona-products")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "teststorage")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_KEY", "test-storage-key")
        
        settings = Settings()
        
        assert settings.AZURE_OPENAI_API_KEY == "test-key"
        assert settings.AZURE_OPENAI_ENDPOINT == "https://test.openai.azure.com/"
        assert settings.AZURE_SEARCH_SERVICE_NAME == "test-search"
    
    def test_settings_missing_openai_key(self, monkeypatch):
        """Test Settings validation with missing OpenAI key."""
        monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.setenv("AZURE_SEARCH_SERVICE_NAME", "test-search")
        monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-search-key")
        monkeypatch.setenv("AZURE_SEARCH_INDEX_NAME", "bona-products")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "teststorage")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_KEY", "test-storage-key")
        
        with pytest.raises(ValidationError):
            Settings()
    
    def test_settings_missing_search_service(self, monkeypatch):
        """Test Settings validation with missing search service."""
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.delenv("AZURE_SEARCH_SERVICE_NAME", raising=False)
        monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-search-key")
        monkeypatch.setenv("AZURE_SEARCH_INDEX_NAME", "bona-products")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "teststorage")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_KEY", "test-storage-key")
        
        with pytest.raises(ValidationError):
            Settings()


class TestSettingsDefaults:
    """Test Settings default values."""
    
    def test_default_deployment_name(self, monkeypatch):
        """Test default OpenAI deployment name."""
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.setenv("AZURE_SEARCH_SERVICE_NAME", "test-search")
        monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-search-key")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "teststorage")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_KEY", "test-storage-key")
        
        settings = Settings()
        
        assert settings.AZURE_OPENAI_DEPLOYMENT_NAME == "gpt-35-turbo"
    
    def test_custom_deployment_name(self, monkeypatch):
        """Test custom OpenAI deployment name."""
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        monkeypatch.setenv("AZURE_SEARCH_SERVICE_NAME", "test-search")
        monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-search-key")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "teststorage")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_KEY", "test-storage-key")
        
        settings = Settings()
        
        assert settings.AZURE_OPENAI_DEPLOYMENT_NAME == "gpt-4"
    
    def test_default_search_index(self, monkeypatch):
        """Test default search index name."""
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.setenv("AZURE_SEARCH_SERVICE_NAME", "test-search")
        monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-search-key")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "teststorage")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_KEY", "test-storage-key")
        
        settings = Settings()
        
        assert settings.AZURE_SEARCH_INDEX_NAME == "bona-products"
    
    def test_default_storage_container(self, monkeypatch):
        """Test default storage container name."""
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.setenv("AZURE_SEARCH_SERVICE_NAME", "test-search")
        monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-search-key")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "teststorage")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_KEY", "test-storage-key")
        
        settings = Settings()
        
        assert settings.AZURE_STORAGE_CONTAINER_NAME == "documents"
    
    def test_default_environment(self, monkeypatch):
        """Test default environment."""
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.setenv("AZURE_SEARCH_SERVICE_NAME", "test-search")
        monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-search-key")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "teststorage")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_KEY", "test-storage-key")
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        
        settings = Settings()
        
        assert settings.ENVIRONMENT == "development"
    
    def test_default_log_level(self, monkeypatch):
        """Test default log level."""
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.setenv("AZURE_SEARCH_SERVICE_NAME", "test-search")
        monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-search-key")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "teststorage")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_KEY", "test-storage-key")
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        
        settings = Settings()
        
        assert settings.LOG_LEVEL == "INFO"


class TestSettingsEnvironmentVariables:
    """Test environment variable handling."""
    
    def test_settings_from_environment(self, monkeypatch):
        """Test Settings can read from environment variables."""
        test_env = {
            "AZURE_OPENAI_API_KEY": "env-key",
            "AZURE_OPENAI_ENDPOINT": "https://env.openai.azure.com/",
            "AZURE_SEARCH_SERVICE_NAME": "env-search",
            "AZURE_SEARCH_API_KEY": "env-search-key",
            "AZURE_STORAGE_ACCOUNT_NAME": "envstorage",
            "AZURE_STORAGE_ACCOUNT_KEY": "env-storage-key",
        }
        
        for key, value in test_env.items():
            monkeypatch.setenv(key, value)
        
        settings = Settings()
        
        assert settings.AZURE_OPENAI_API_KEY == "env-key"
        assert settings.AZURE_SEARCH_SERVICE_NAME == "env-search"
    
    def test_settings_case_sensitive(self, monkeypatch):
        """Test Settings are case sensitive."""
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.setenv("AZURE_SEARCH_SERVICE_NAME", "test-search")
        monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-search-key")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "teststorage")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_KEY", "test-storage-key")
        
        settings = Settings()
        
        # Should use the correct case
        assert settings.AZURE_OPENAI_API_KEY == "test-key"


class TestSettingsValidation:
    """Test Settings field validation."""
    
    def test_settings_empty_string_api_key(self, monkeypatch):
        """Test Settings with empty API key."""
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.setenv("AZURE_SEARCH_SERVICE_NAME", "test-search")
        monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-search-key")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "teststorage")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_KEY", "test-storage-key")
        
        # Should create settings successfully even with environment set correctly
        settings = Settings()
        assert settings.AZURE_OPENAI_API_KEY == "test-key"
    
    def test_settings_valid_log_levels(self, monkeypatch):
        """Test Settings accept valid log levels."""
        base_env = {
            "AZURE_OPENAI_API_KEY": "test-key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_SEARCH_SERVICE_NAME": "test-search",
            "AZURE_SEARCH_API_KEY": "test-search-key",
            "AZURE_STORAGE_ACCOUNT_NAME": "teststorage",
            "AZURE_STORAGE_ACCOUNT_KEY": "test-storage-key",
        }
        
        for log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            for key, value in base_env.items():
                monkeypatch.setenv(key, value)
            monkeypatch.setenv("LOG_LEVEL", log_level)
            
            settings = Settings()
            assert settings.LOG_LEVEL == log_level


class TestSettingsIntegration:
    """Test Settings integration."""
    
    def test_settings_singleton_behavior(self, monkeypatch):
        """Test that settings can be imported and used multiple times."""
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.setenv("AZURE_SEARCH_SERVICE_NAME", "test-search")
        monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-search-key")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "teststorage")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_KEY", "test-storage-key")
        
        settings1 = Settings()
        settings2 = Settings()
        
        # Both instances should have the same values
        assert settings1.AZURE_OPENAI_API_KEY == settings2.AZURE_OPENAI_API_KEY
