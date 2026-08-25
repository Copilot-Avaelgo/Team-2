import logging
import os
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Service for processing and chunking TXT documents"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        """
        Initialize document processor
        
        Args:
            chunk_size: Number of words per chunk
            overlap: Number of words to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def process_documents_from_folder(self, folder_path: str) -> List[Dict[str, str]]:
        """
        Process all TXT files from a folder
        
        Args:
            folder_path: Path to folder containing TXT files
            
        Returns:
            List of document dicts with id, content, source
        """
        documents = []
        folder = Path(folder_path)
        
        if not folder.exists():
            logger.error(f"Folder not found: {folder_path}")
            return documents
        
        txt_files = list(folder.glob("*.txt"))
        logger.info(f"Found {len(txt_files)} TXT files in {folder_path}")
        
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                chunks = self._chunk_text(content, file_path.name)
                documents.extend(chunks)
                logger.info(f"Processed {file_path.name}: {len(chunks)} chunks created")
                
            except Exception as e:
                logger.error(f"Error processing {file_path.name}: {e}")
                continue
        
        logger.info(f"Total documents created: {len(documents)}")
        return documents
    
    def _chunk_text(self, text: str, source: str) -> List[Dict[str, str]]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Full document text
            source: Document source/filename
            
        Returns:
            List of chunk dicts
        """
        words = text.split()
        chunks = []
        chunk_id = 0
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            end_idx = min(i + self.chunk_size, len(words))
            chunk_text = " ".join(words[i:end_idx])
            
            if len(chunk_text.strip()) > 0:
                chunks.append({
                    "id": f"{source}_{chunk_id}",
                    "content": chunk_text,
                    "source": source
                })
                chunk_id += 1
        
        return chunks
    
    def load_and_process(self, folder_path: str) -> List[Dict[str, str]]:
        """
        Load and process all documents from folder
        
        Args:
            folder_path: Path to folder with TXT files
            
        Returns:
            List of processed documents
        """
        return self.process_documents_from_folder(folder_path)
