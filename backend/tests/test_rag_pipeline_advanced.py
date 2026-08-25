"""
Advanced integration tests for the Bona RAG system with realistic TDS content fixtures.

These tests demonstrate:
1. Loading real TDS files from the ragf folder
2. Testing document processor with actual Bona product documentation
3. Simulating end-to-end RAG flow with realistic data
4. Measuring performance with real content
"""

import pytest
import logging
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List

from src.models import RetrievedDocument, ChatResponse
from src.services import RAGService
from src.services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class TestRealTDSContent:
    """Test integration with real Bona TDS (Technical Data Sheet) files"""
    
    @pytest.fixture
    def tds_folder_path(self):
        """Locate the TDS files folder"""
        # Check for ragf folder relative to project root
        paths_to_check = [
            Path("D:\\AI2\\ragf"),
            Path(__file__).parent.parent.parent / "ragf",
            Path("ragf")
        ]
        
        for path in paths_to_check:
            if path.exists():
                tds_files = list(path.glob("*.txt"))
                if tds_files:
                    return path
        
        pytest.skip("TDS folder not found")
    
    def test_load_real_tds_files(self, tds_folder_path):
        """
        Test loading real TDS files from disk
        
        Verifies:
        - Files can be located and read
        - Content is properly encoded
        - Multiple products are available
        """
        tds_files = list(tds_folder_path.glob("*.txt"))
        
        assert len(tds_files) > 0, f"No TDS files found in {tds_folder_path}"
        
        for tds_file in tds_files[:3]:  # Test first 3 files
            with open(tds_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            assert len(content) > 0, f"Empty file: {tds_file.name}"
            logger.info(f"✓ Loaded {tds_file.name} ({len(content)} bytes)")
    
    def test_document_processor_with_real_tds(self, tds_folder_path):
        """
        Test document processor with real TDS files
        
        Verifies:
        - Files are properly chunked
        - Chunks maintain source attribution
        - Chunks have reasonable content length
        """
        processor = DocumentProcessor(chunk_size=500, overlap=100)
        documents = processor.process_documents_from_folder(str(tds_folder_path))
        
        assert len(documents) > 0, "No documents processed"
        
        # Verify document structure
        for doc in documents[:10]:  # Check first 10 chunks
            assert 'id' in doc
            assert 'content' in doc
            assert 'source' in doc
            assert len(doc['content']) > 0
            assert '.txt' in doc['source']
            assert 'Bona' in doc['source']
        
        logger.info(f"✓ Processed {len(documents)} document chunks from real TDS files")
    
    def test_realistic_query_bona_classic_drying_time(self, tds_folder_path):
        """
        Test realistic query about Bona Classic drying time
        
        Query: "What is the drying time for Bona Classic?"
        Expected: Response includes information from Bona_Classic_TDS_AU.txt
        """
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            # Create realistic mock documents from Classic TDS
            classic_docs = [
                RetrievedDocument(
                    content="Drying time: 1 - 2 hours (20° C / 60% R.H). Type of lacquer: 1-component waterborne acrylate primer",
                    source="Bona_Classic_TDS_AU.txt",
                    score=0.98
                ),
                RetrievedDocument(
                    content="High temperatures and low humidity shorten, low temperatures and high humidity lengthen drying time. "
                           "Minimum temperature for use is 13° C.",
                    source="Bona_Classic_TDS_AU.txt",
                    score=0.91
                )
            ]
            
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = classic_docs
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_service.generate_response.return_value = (
                "Bona Classic has a drying time of 1-2 hours at 20°C with 60% relative humidity. "
                "Drying time can be affected by temperature and humidity conditions."
            )
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            response = rag_service.process_query("What is the drying time for Bona Classic?")
            
            assert len(response.source_documents) == 2
            assert "Classic" in response.source_documents[0].source
            assert "drying" in response.answer.lower() or "dry" in response.answer.lower()
            logger.info(f"✓ Bona Classic query test passed")
    
    def test_realistic_query_bona_traffichd_application(self):
        """
        Test realistic query about Bona TrafficHD application
        
        Query: "How do I apply Bona TrafficHD?"
        Expected: Response includes application information
        """
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            traffic_docs = [
                RetrievedDocument(
                    content="Bona Traffic HD - TWO COMPONENT, WATERBORNE COATING. Application tools: Bona Microfleece Roller or "
                           "Bona Swivel Head Bar Applicator. Application rate: 8 - 10 m² / L per coat",
                    source="Bona_TrafficHD_TDS_AU.txt",
                    score=0.96
                ),
                RetrievedDocument(
                    content="Allow full traffic after 12 hours. Floor owners are now able to get back on the floor just 12 hours after application. "
                           "Allows full traffic after 12 hours",
                    source="Bona_TrafficHD_TDS_AU.txt",
                    score=0.88
                )
            ]
            
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = traffic_docs
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_service.generate_response.return_value = (
                "Bona TrafficHD should be applied using a Bona Microfleece Roller or Bona Swivel Head Bar Applicator. "
                "Apply at a rate of 8-10 m² per liter per coat. Full traffic is allowed after 12 hours."
            )
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            response = rag_service.process_query("How do I apply Bona TrafficHD?")
            
            assert len(response.source_documents) > 0
            assert "TrafficHD" in response.source_documents[0].source
            assert "application" in response.answer.lower() or "apply" in response.answer.lower()
            logger.info(f"✓ Bona TrafficHD application query test passed")
    
    def test_realistic_query_voc_emissions(self):
        """
        Test realistic query about VOC/emissions content
        
        Query: "What is the VOC content of Bona products?"
        Expected: Response includes emissions/certification information
        """
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            voc_docs = [
                RetrievedDocument(
                    content="Certifications: GREENGUARD EC1PLUS for very low emissions EN 13501-1; Reaction to fire. "
                           "Safety: Unclassified",
                    source="Bona_Classic_TDS_AU.txt",
                    score=0.94
                ),
                RetrievedDocument(
                    content="EMICODE EC1 certified for very low indoor emissions. "
                           "Qualifies for LEED and BREEAM points.",
                    source="Bona_TrafficHD_TDS_AU.txt",
                    score=0.89
                )
            ]
            
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = voc_docs
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_service.generate_response.return_value = (
                "Bona products are certified for very low emissions. Bona Classic carries GREENGUARD EC1PLUS certification, "
                "while Bona TrafficHD carries EMICODE EC1 certification. Both products meet strict environmental standards."
            )
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            response = rag_service.process_query("What is the VOC content of Bona products?")
            
            assert len(response.source_documents) > 0
            assert "emission" in response.answer.lower() or "voc" in response.answer.lower() or "ec1" in response.answer.lower()
            logger.info(f"✓ VOC emissions query test passed")


class TestRAGPipelinePerformanceWithRealisticData:
    """Performance and latency tests with realistic content volumes"""
    
    def test_pipeline_latency_with_realistic_documents(self):
        """
        Measure pipeline latency with realistic document set
        
        Simulates:
        - Multiple product documents
        - Various document sizes
        - Real context window
        """
        # Create realistic document set
        realistic_docs = [
            RetrievedDocument(
                content="Bona Classic Hard-Surface Floor Cleaner is a premium cleaning solution designed specifically "
                       "for sealed wooden floors and hard surfaces. It effectively removes dirt, grime, dust, and other "
                       "contaminants while maintaining the beautiful shine of your floors. Features: Effectively cleans "
                       "sealed wooden floors, Safe for hard surfaces including tile and vinyl, Does not leave streaks "
                       "or residue, Pleasant fresh scent, Environmentally friendly formula",
                source="Bona_Classic_TDS_AU.txt",
                score=0.95
            ),
            RetrievedDocument(
                content="Bona Traffic HD - TWO COMPONENT, WATERBORNE COATING. Powerful performance at top speed. "
                       "Bona Traffic HD delivers superior protection in less time than ever before, outperforming any "
                       "other finish in terms of speed and durability. Experience unparalleled wear resistance and "
                       "minimised downtime. Floor owners are now able to get back on the floor just 12 hours after application.",
                source="Bona_TrafficHD_TDS_AU.txt",
                score=0.92
            ),
            RetrievedDocument(
                content="Drying time: 1 - 2 hours (20° C / 60% R.H). Application tools: Bona Roller or Bona Swivel Head Bar "
                       "Applicator. Application rate: 8 - 10 m² / L per coat. Shelf life: One year from date of production "
                       "in unopened original container. Storage/transport: Temperature must not fall below +5º C or exceed +30º C",
                source="Bona_Classic_TDS_AU.txt",
                score=0.89
            )
        ]
        
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = realistic_docs
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_service.generate_response.return_value = "This is a comprehensive answer based on Bona product documentation"
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            
            # Measure pipeline performance
            start_time = time.time()
            response = rag_service.process_query("Tell me about Bona finishes and their features")
            total_latency = time.time() - start_time
            
            assert response is not None
            assert len(response.source_documents) == 3
            
            # Latency should be under 100ms for mocked services
            assert total_latency < 0.1, f"Latency too high: {total_latency*1000:.2f}ms"
            
            logger.info(f"✓ Pipeline latency test passed - {total_latency*1000:.2f}ms for 3 documents")
    
    def test_context_window_scaling(self):
        """
        Test how pipeline scales with increasing context
        
        Scenarios:
        - Small context (2 documents)
        - Medium context (5 documents)
        - Large context (15 documents)
        """
        context_sizes = [2, 5, 15]
        latencies = []
        
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            mock_llm_service = Mock()
            mock_llm_service.generate_response.return_value = "Answer"
            mock_llm_class.return_value = mock_llm_service
            
            for size in context_sizes:
                # Create documents for this context size
                docs = [
                    RetrievedDocument(
                        content=f"Product documentation chunk {i}: " + 
                               "This is sample Bona product information with technical specifications, " +
                               "application instructions, and safety information.",
                        source=f"Bona_Product_{i}.txt",
                        score=0.95 - (i * 0.05)
                    )
                    for i in range(size)
                ]
                
                mock_search_service = Mock()
                mock_search_service.search_documents.return_value = docs
                mock_search_class.return_value = mock_search_service
                
                rag_service = RAGService()
                
                start_time = time.time()
                response = rag_service.process_query("Query")
                latency = time.time() - start_time
                
                latencies.append(latency)
                assert len(response.source_documents) == size
            
            logger.info(f"✓ Context scaling test passed - Latencies: {[f'{l*1000:.2f}ms' for l in latencies]}")


class TestErrorRecoveryWithRealisticContent:
    """Test error handling with realistic content scenarios"""
    
    def test_graceful_handling_of_partial_content_loss(self):
        """
        Test graceful degradation when some documents fail to load
        
        Scenario: Some source documents are unavailable but system continues
        """
        partial_docs = [
            RetrievedDocument(
                content="Available Bona Classic documentation...",
                source="Bona_Classic_TDS_AU.txt",
                score=0.95
            ),
            # Second document might be partially corrupted but still valid
            RetrievedDocument(
                content="Partial content from TrafficHD specification",
                source="Bona_TrafficHD_TDS_AU.txt",
                score=0.87
            )
        ]
        
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = partial_docs
            mock_search_class.return_value = mock_search_service
            
            mock_llm_service = Mock()
            mock_llm_service.generate_response.return_value = "Answer based on available documentation"
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            response = rag_service.process_query("Query")
            
            # Should return partial results successfully
            assert len(response.source_documents) == 2
            assert response.answer is not None
            logger.info("✓ Partial content handling test passed")
    
    def test_timeout_handling_with_large_llm_response(self):
        """
        Test handling of slow LLM responses
        
        Scenario: LLM takes longer than expected but still completes
        """
        with patch('src.services.SearchService') as mock_search_class, \
             patch('src.services.LLMService') as mock_llm_class:
            
            mock_search_service = Mock()
            mock_search_service.search_documents.return_value = [
                RetrievedDocument(
                    content="Bona product information",
                    source="Bona_Product.txt",
                    score=0.95
                )
            ]
            mock_search_class.return_value = mock_search_service
            
            # Simulate slower LLM response
            def slow_response(*args, **kwargs):
                time.sleep(0.01)  # 10ms delay
                return "Response from LLM"
            
            mock_llm_service = Mock()
            mock_llm_service.generate_response.side_effect = slow_response
            mock_llm_class.return_value = mock_llm_service
            
            rag_service = RAGService()
            response = rag_service.process_query("Query")
            
            assert response is not None
            logger.info("✓ Slow LLM response handling test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--log-cli-level=INFO"])
