import logging
from typing import List
from src.services.search_service import SearchService
from src.services.llm_service import LLMService
from src.services.document_processor import DocumentProcessor
from src.models import ChatResponse, RetrievedDocument

logger = logging.getLogger(__name__)


class RAGService:
    """Orchestrates the complete RAG pipeline"""
    
    def __init__(self):
        try:
            self.search_service = SearchService()
            self.llm_service = LLMService()
            self.doc_processor = DocumentProcessor()
            logger.info("RAG Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG Service: {e}")
            raise
    
    def process_query(self, query: str, session_id: str = None) -> ChatResponse:
        """
        Process user query through complete RAG pipeline
        
        Args:
            query: User question
            session_id: Optional session identifier
            
        Returns:
            ChatResponse with answer and source documents
        """
        try:
            logger.info(f"Processing query: {query[:50]}...")
            
            # Step 1: Retrieve relevant documents
            retrieved_docs = self.search_service.search_documents(query, top_k=5)
            
            if not retrieved_docs:
                logger.warning(f"No documents retrieved for query: {query}")
                return ChatResponse(
                    answer="I couldn't find relevant product documentation to answer your question. Please try a different query.",
                    source_documents=[],
                    session_id=session_id
                )
            
            # Step 2: Generate response using LLM
            answer = self.llm_service.generate_response(query, retrieved_docs)
            
            # Step 3: Return response with sources
            response = ChatResponse(
                answer=answer,
                source_documents=retrieved_docs,
                session_id=session_id
            )
            
            logger.info(f"Query processed successfully, returned {len(retrieved_docs)} source documents")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise
    
    def initialize_knowledge_base(self, documents_folder: str) -> bool:
        """
        Initialize knowledge base by processing and indexing documents
        
        Args:
            documents_folder: Path to folder with TXT documents
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Initializing knowledge base from: {documents_folder}")
            
            # Process documents
            documents = self.doc_processor.load_and_process(documents_folder)
            
            if not documents:
                logger.warning(f"No documents found in {documents_folder}")
                return False
            
            # Index documents
            self.search_service.index_documents(documents)
            
            logger.info(f"Knowledge base initialized with {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {e}")
            raise
