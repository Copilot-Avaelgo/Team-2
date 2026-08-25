import logging
from typing import List
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from src.config import settings
from src.models import RetrievedDocument

logger = logging.getLogger(__name__)


class SearchService:
    """Service for interacting with Azure Cognitive Search"""
    
    def __init__(self):
        try:
            self.search_client = SearchClient(
                endpoint=f"https://{settings.AZURE_SEARCH_SERVICE_NAME}.search.windows.net",
                index_name=settings.AZURE_SEARCH_INDEX_NAME,
                credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY)
            )
            logger.info(f"Initialized Cognitive Search client for index: {settings.AZURE_SEARCH_INDEX_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize Cognitive Search: {e}")
            raise
    
    def search_documents(self, query: str, top_k: int = 5) -> List[RetrievedDocument]:
        """
        Search Cognitive Search index for relevant documents
        
        Args:
            query: User search query
            top_k: Number of top results to return
            
        Returns:
            List of RetrievedDocument objects
        """
        try:
            results = self.search_client.search(
                search_text=query,
                top=top_k,
                select=["content", "source"]
            )
            
            documents = []
            for result in results:
                documents.append(
                    RetrievedDocument(
                        content=result["content"],
                        source=result.get("source", "unknown"),
                        score=result.get("@search.score", 0.0)
                    )
                )
            
            logger.info(f"Retrieved {len(documents)} documents for query: {query[:50]}...")
            return documents
            
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            raise
    
    def index_documents(self, documents: List[dict]) -> bool:
        """
        Upload documents to Cognitive Search index
        
        Args:
            documents: List of document dicts with 'id', 'content', 'source'
            
        Returns:
            True if successful
        """
        try:
            result = self.search_client.upload_documents(documents=documents)
            logger.info(f"Uploaded {len(documents)} documents to Cognitive Search")
            return True
        except Exception as e:
            logger.error(f"Failed to index documents: {e}")
            raise
