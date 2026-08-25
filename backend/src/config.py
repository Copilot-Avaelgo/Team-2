import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Azure and LLM configuration"""
    
    # Azure OpenAI
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-35-turbo"
    
    # Azure Cognitive Search
    AZURE_SEARCH_SERVICE_NAME: str
    AZURE_SEARCH_API_KEY: str
    AZURE_SEARCH_INDEX_NAME: str = "bona-products"
    
    # Azure Blob Storage
    AZURE_STORAGE_ACCOUNT_NAME: str
    AZURE_STORAGE_ACCOUNT_KEY: str
    AZURE_STORAGE_CONTAINER_NAME: str = "documents"
    
    # App settings
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
