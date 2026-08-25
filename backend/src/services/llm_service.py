import logging
from typing import List
from openai import AzureOpenAI
from src.config import settings
from src.models import RetrievedDocument

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with Azure OpenAI"""
    
    def __init__(self):
        try:
            self.client = AzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version="2023-12-01-preview",
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME
            logger.info(f"Initialized Azure OpenAI client with deployment: {self.deployment_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI: {e}")
            raise
    
    def generate_response(
        self, 
        query: str, 
        context_documents: List[RetrievedDocument],
        max_tokens: int = 512
    ) -> str:
        """
        Generate RAG response using Azure OpenAI
        
        Args:
            query: User query
            context_documents: Retrieved documents from Cognitive Search
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
        """
        try:
            # Build context from retrieved documents
            context = self._build_context(context_documents)
            
            # Create RAG prompt
            prompt = self._create_prompt(query, context)
            
            # Call Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant for Bona flooring products. Answer questions based on the provided product documentation. If you don't know the answer, say so."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=max_tokens,
                top_p=0.95
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated response for query: {query[:50]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise
    
    def _build_context(self, documents: List[RetrievedDocument]) -> str:
        """Build context string from retrieved documents"""
        if not documents:
            return "No relevant product documentation found."
        
        context_parts = []
        for doc in documents:
            context_parts.append(f"Source: {doc.source}\n{doc.content}\n")
        
        return "\n---\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create RAG prompt with context"""
        return f"""Based on the following Bona product documentation, answer the user's question:

DOCUMENTATION:
{context}

USER QUESTION:
{query}

ANSWER:"""
