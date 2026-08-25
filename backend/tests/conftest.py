"""Shared pytest fixtures and configurations."""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
from src.models import RetrievedDocument

# Set environment variables for testing BEFORE importing config
os.environ["AZURE_OPENAI_API_KEY"] = "test-key"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-35-turbo"
os.environ["AZURE_SEARCH_SERVICE_NAME"] = "test-search"
os.environ["AZURE_SEARCH_API_KEY"] = "test-search-key"
os.environ["AZURE_SEARCH_INDEX_NAME"] = "bona-products"
os.environ["AZURE_STORAGE_ACCOUNT_NAME"] = "teststorage"
os.environ["AZURE_STORAGE_ACCOUNT_KEY"] = "test-storage-key"
os.environ["AZURE_STORAGE_CONTAINER_NAME"] = "documents"
os.environ["ENVIRONMENT"] = "test"
os.environ["LOG_LEVEL"] = "DEBUG"


# Set environment variables for testing
@pytest.fixture(scope="session", autouse=True)
def setup_env():
    """Set up environment variables for testing."""
    os.environ["AZURE_OPENAI_API_KEY"] = "test-key"
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
    os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-35-turbo"
    os.environ["AZURE_SEARCH_SERVICE_NAME"] = "test-search"
    os.environ["AZURE_SEARCH_API_KEY"] = "test-search-key"
    os.environ["AZURE_SEARCH_INDEX_NAME"] = "bona-products"
    os.environ["AZURE_STORAGE_ACCOUNT_NAME"] = "teststorage"
    os.environ["AZURE_STORAGE_ACCOUNT_KEY"] = "test-storage-key"
    os.environ["AZURE_STORAGE_CONTAINER_NAME"] = "documents"
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"


@pytest.fixture
def sample_documents():
    """Provide sample documents for testing."""
    return [
        {
            "id": "doc1_0",
            "content": "Bona Hard-Surface Floor Cleaner is designed for sealed wooden floors and hard surfaces. It removes dirt and grime effectively while maintaining the shine of your floor.",
            "source": "Bona_Cleaner_Manual.txt"
        },
        {
            "id": "doc1_1",
            "content": "Apply the cleaner directly to a microfiber pad and mop the floor. Do not use on unsealed wood. Allow 15 minutes drying time.",
            "source": "Bona_Cleaner_Manual.txt"
        },
        {
            "id": "doc2_0",
            "content": "Bona Hard-Surface Floor Finish provides a protective coating for wooden and vinyl floors. It enhances the natural beauty of your floors with a beautiful gloss finish.",
            "source": "Bona_Finish_Manual.txt"
        }
    ]


@pytest.fixture
def sample_text():
    """Provide sample text for chunking tests."""
    text = """Bona Classic Hard-Surface Floor Cleaner
    
The Bona Hard-Surface Floor Cleaner is a premium cleaning solution designed specifically for sealed wooden floors and hard surfaces. 
It effectively removes dirt, grime, dust, and other contaminants while maintaining the beautiful shine of your floors.

Key Features:
- Effectively cleans sealed wooden floors
- Safe for hard surfaces including tile and vinyl
- Does not leave streaks or residue
- Pleasant fresh scent
- Environmentally friendly formula

Application Instructions:
Apply the cleaner directly to a microfiber pad and mop the floor in circular motions. 
For stubborn stains, allow the cleaner to sit for a few minutes before wiping. 
Do not use on unsealed or wax-finished wood. Allow 15 minutes drying time before heavy foot traffic.

Safety Information:
Keep out of reach of children and pets. In case of eye contact, rinse with water for 15 minutes.
If ingested, contact poison control immediately."""
    
    return text


@pytest.fixture
def sample_retrieved_documents():
    """Provide sample retrieved documents for LLM tests."""
    return [
        RetrievedDocument(
            content="Bona Classic drying time is 6-8 hours between coats.",
            source="Bona_Classic_TDS.txt",
            score=0.95
        ),
        RetrievedDocument(
            content="For best results, apply 2-3 coats of Bona Classic finish.",
            source="Bona_Application_Guide.txt",
            score=0.87
        )
    ]


@pytest.fixture
def mock_azure_search_client():
    """Provide a mock Azure Cognitive Search client."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def mock_azure_openai_client():
    """Provide a mock Azure OpenAI client."""
    mock_client = MagicMock()
    
    # Mock the chat completion response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Bona Classic has a drying time of 6-8 hours between coats."
    mock_client.chat.completions.create.return_value = mock_response
    
    return mock_client


@pytest.fixture
def temp_documents_folder(tmp_path):
    """Create a temporary folder with sample TXT files for testing."""
    # Create sample document files
    doc1 = tmp_path / "product_guide.txt"
    doc1.write_text("""Bona Hard-Surface Floor Finish

Features and Benefits:
- Premium quality finish for wooden floors
- Excellent durability and protection
- Beautiful high-gloss appearance
- Easy application process

Application:
Apply thin, even coats using a microfiber applicator pad. 
Allow 4-6 hours drying time between coats.
Final curing time is 24 hours.""")
    
    doc2 = tmp_path / "cleaning_guide.txt"
    doc2.write_text("""Bona Hard-Surface Floor Cleaner

How to Use:
1. Dampen microfiber pad with cleaner
2. Mop floor in circular motions
3. Do not saturate the floor
4. Allow 15 minutes drying time

Safety:
- Keep away from children and pets
- Rinse thoroughly with water if ingested
- Use in well-ventilated area""")
    
    return tmp_path


@pytest.fixture
def mock_settings():
    """Provide mock settings for testing."""
    mock_settings = MagicMock()
    mock_settings.AZURE_OPENAI_API_KEY = "test-key"
    mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
    mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
    mock_settings.AZURE_SEARCH_SERVICE_NAME = "test-search"
    mock_settings.AZURE_SEARCH_API_KEY = "test-search-key"
    mock_settings.AZURE_SEARCH_INDEX_NAME = "bona-products"
    
    return mock_settings


@pytest.fixture
def sample_query_response():
    """Provide a sample query response."""
    return "Bona Classic has a drying time of 6-8 hours between coats."


@pytest.fixture
def empty_documents():
    """Provide empty document list."""
    return []


@pytest.fixture
def large_document_set():
    """Provide a large set of documents for stress testing."""
    return [
        RetrievedDocument(
            content=f"Product information about Bona product {i}. This is sample content for testing large document sets.",
            source=f"bona_product_{i}.txt",
            score=0.95 - (i * 0.01)  # Decreasing scores
        )
        for i in range(50)
    ]


@pytest.fixture
def sample_query_response():
    """Sample RAG pipeline response"""
    from src.models import ChatResponse
    return ChatResponse(
        answer="Bona Classic has a drying time of 1-2 hours at 20°C with 60% relative humidity. "
               "It is a waterborne primer with elastic properties and high solids content, suitable "
               "for practically all types of wood. Application rate is 8-10 m²/L per coat.",
        source_documents=[
            RetrievedDocument(
                content="Drying time: 1 - 2 hours (20° C / 60% R.H)",
                source="Bona_Classic_TDS_AU.txt",
                score=0.95
            )
        ],
        session_id="test-session-123"
    )


@pytest.fixture
def large_document_set():
    """Generate a large set of documents for testing context handling"""
    documents = []
    for i in range(10):
        documents.append(
            RetrievedDocument(
                content=f"Document chunk {i}: This is sample product documentation content about Bona finishes "
                       f"and their specifications including application rates, drying times, and technical data. "
                       f"Product information chunk number {i} containing technical specifications.",
                source=f"Bona_Product_TDS_AU_{i}.txt",
                score=0.9 - (i * 0.05)
            )
        )
    return documents


@pytest.fixture
def empty_documents():
    """Empty document list for testing no-match scenarios"""
    return []
