"""Tests for document processor service."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from src.services.document_processor import DocumentProcessor


class TestDocumentProcessorInitialization:
    """Test DocumentProcessor initialization."""
    
    def test_init_with_default_values(self):
        """Test initialization with default chunk size and overlap."""
        processor = DocumentProcessor()
        assert processor.chunk_size == 500
        assert processor.overlap == 100
    
    def test_init_with_custom_values(self):
        """Test initialization with custom chunk size and overlap."""
        processor = DocumentProcessor(chunk_size=1000, overlap=200)
        assert processor.chunk_size == 1000
        assert processor.overlap == 200
    
    def test_init_with_zero_overlap(self):
        """Test initialization with zero overlap."""
        processor = DocumentProcessor(chunk_size=500, overlap=0)
        assert processor.overlap == 0


class TestChunkingLogic:
    """Test text chunking functionality."""
    
    def test_chunk_text_basic(self, sample_text):
        """Test basic text chunking."""
        processor = DocumentProcessor(chunk_size=50, overlap=10)
        chunks = processor._chunk_text(sample_text, "test.txt")
        
        assert len(chunks) > 0
        assert all("id" in chunk for chunk in chunks)
        assert all("content" in chunk for chunk in chunks)
        assert all("source" in chunk for chunk in chunks)
    
    def test_chunk_text_ids(self, sample_text):
        """Test that chunk IDs are correctly formatted."""
        processor = DocumentProcessor(chunk_size=50, overlap=10)
        chunks = processor._chunk_text(sample_text, "document.txt")
        
        for i, chunk in enumerate(chunks):
            assert chunk["id"] == f"document.txt_{i}"
            assert chunk["source"] == "document.txt"
    
    def test_chunk_text_overlap_handling(self, sample_text):
        """Test that overlapping chunks share content."""
        processor = DocumentProcessor(chunk_size=20, overlap=5)
        chunks = processor._chunk_text(sample_text, "test.txt")
        
        # Verify overlap - last 5 words of chunk i should be in chunk i+1
        for i in range(len(chunks) - 1):
            current_content = chunks[i]["content"]
            next_content = chunks[i + 1]["content"]
            
            # Verify there's some word overlap
            current_words = set(current_content.split())
            next_words = set(next_content.split())
            overlap_words = current_words & next_words
            
            assert len(overlap_words) > 0, f"No overlap found between chunk {i} and {i+1}"
    
    def test_chunk_text_empty_string(self):
        """Test chunking empty string."""
        processor = DocumentProcessor()
        chunks = processor._chunk_text("", "empty.txt")
        
        assert len(chunks) == 0
    
    def test_chunk_text_single_word(self):
        """Test chunking single word."""
        processor = DocumentProcessor()
        chunks = processor._chunk_text("single", "test.txt")
        
        assert len(chunks) == 1
        assert chunks[0]["content"] == "single"
    
    def test_chunk_text_preserves_content(self, sample_text):
        """Test that chunking doesn't lose content."""
        processor = DocumentProcessor(chunk_size=100, overlap=20)
        chunks = processor._chunk_text(sample_text, "test.txt")
        
        # Reconstruct text without overlaps to verify coverage
        reconstructed_words = set()
        for chunk in chunks:
            reconstructed_words.update(chunk["content"].split())
        
        original_words = set(sample_text.split())
        assert len(reconstructed_words) >= len(original_words) * 0.95  # Allow small loss due to word boundaries


class TestProcessDocumentsFromFolder:
    """Test processing documents from a folder."""
    
    def test_process_documents_from_valid_folder(self, temp_documents_folder):
        """Test processing documents from valid folder."""
        processor = DocumentProcessor(chunk_size=50, overlap=10)
        documents = processor.process_documents_from_folder(str(temp_documents_folder))
        
        assert len(documents) > 0
        assert all("id" in doc for doc in documents)
        assert all("content" in doc for doc in documents)
        assert all("source" in doc for doc in documents)
    
    def test_process_documents_multiple_files(self, temp_documents_folder):
        """Test processing multiple files from folder."""
        processor = DocumentProcessor(chunk_size=50, overlap=10)
        documents = processor.process_documents_from_folder(str(temp_documents_folder))
        
        # Should have processed at least 2 files (product_guide.txt and cleaning_guide.txt)
        sources = set(doc["source"] for doc in documents)
        assert len(sources) >= 2
    
    def test_process_documents_nonexistent_folder(self):
        """Test processing from non-existent folder."""
        processor = DocumentProcessor()
        documents = processor.process_documents_from_folder("/nonexistent/folder/path")
        
        assert len(documents) == 0
    
    def test_process_documents_empty_folder(self, tmp_path):
        """Test processing from empty folder."""
        processor = DocumentProcessor()
        documents = processor.process_documents_from_folder(str(tmp_path))
        
        assert len(documents) == 0
    
    def test_process_documents_only_txt_files(self, tmp_path):
        """Test that only TXT files are processed."""
        # Create various file types
        (tmp_path / "document.txt").write_text("content")
        (tmp_path / "image.png").write_bytes(b"fake image")
        (tmp_path / "script.py").write_text("print('hello')")
        
        processor = DocumentProcessor(chunk_size=50, overlap=10)
        documents = processor.process_documents_from_folder(str(tmp_path))
        
        # Should only process document.txt
        sources = {doc["source"] for doc in documents}
        assert len(sources) == 1
        assert "document.txt" in sources
    
    def test_process_documents_with_encoding_errors(self, tmp_path):
        """Test processing files with potential encoding issues."""
        # Create a text file
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Valid UTF-8 content")
        
        processor = DocumentProcessor(chunk_size=50, overlap=10)
        documents = processor.process_documents_from_folder(str(tmp_path))
        
        assert len(documents) > 0


class TestLoadAndProcess:
    """Test load_and_process method."""
    
    def test_load_and_process_integration(self, temp_documents_folder):
        """Test load_and_process integration."""
        processor = DocumentProcessor(chunk_size=50, overlap=10)
        documents = processor.load_and_process(str(temp_documents_folder))
        
        assert len(documents) > 0
        assert all("id" in doc for doc in documents)
        assert all("content" in doc for doc in documents)
        assert all("source" in doc for doc in documents)
    
    def test_load_and_process_returns_list(self, temp_documents_folder):
        """Test that load_and_process returns a list."""
        processor = DocumentProcessor()
        result = processor.load_and_process(str(temp_documents_folder))
        
        assert isinstance(result, list)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_large_text_chunking(self):
        """Test chunking very large text."""
        large_text = " ".join(["word"] * 10000)
        processor = DocumentProcessor(chunk_size=100, overlap=20)
        chunks = processor._chunk_text(large_text, "large.txt")
        
        assert len(chunks) > 0
        # Verify all chunks have content
        assert all(len(chunk["content"]) > 0 for chunk in chunks)
    
    def test_chunk_size_smaller_than_overlap(self):
        """Test behavior when overlap is larger than chunk_size."""
        processor = DocumentProcessor(chunk_size=10, overlap=20)
        text = " ".join(["word"] * 50)
        chunks = processor._chunk_text(text, "test.txt")
        
        # With larger overlap than chunk_size, we still produce chunks
        # This is an edge case - the algorithm still works but with different behavior
        assert isinstance(chunks, list)
    
    def test_special_characters_in_content(self):
        """Test handling of special characters."""
        special_text = "Test with special chars: @#$%^&*() \n\t\r émojis: 🎉 unicode: 你好"
        processor = DocumentProcessor(chunk_size=20, overlap=5)
        chunks = processor._chunk_text(special_text, "special.txt")
        
        assert len(chunks) > 0
    
    def test_very_long_words(self):
        """Test handling of very long words."""
        long_word = "a" * 1000
        text = f"{long_word} short word {long_word}"
        processor = DocumentProcessor(chunk_size=100, overlap=20)
        chunks = processor._chunk_text(text, "test.txt")
        
        assert len(chunks) > 0


class TestDocumentStructure:
    """Test document output structure."""
    
    def test_document_dict_structure(self, sample_text):
        """Test that documents have correct structure."""
        processor = DocumentProcessor()
        chunks = processor._chunk_text(sample_text, "test.txt")
        
        for chunk in chunks:
            assert len(chunk) == 3
            assert "id" in chunk
            assert "content" in chunk
            assert "source" in chunk
            assert isinstance(chunk["id"], str)
            assert isinstance(chunk["content"], str)
            assert isinstance(chunk["source"], str)
    
    def test_document_content_not_empty(self, sample_text):
        """Test that document content is never empty."""
        processor = DocumentProcessor(chunk_size=50, overlap=10)
        chunks = processor._chunk_text(sample_text, "test.txt")
        
        assert all(len(chunk["content"].strip()) > 0 for chunk in chunks)
