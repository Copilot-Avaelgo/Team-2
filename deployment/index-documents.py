#!/usr/bin/env python3
"""
Automated Document Indexing for Bona RAG System
Processes TDS files and uploads them to Azure Cognitive Search
Usage: python index-documents.py --service-name <name> --admin-key <key> --docs-path <path>
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Tuple
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DocumentIndexer:
    """Indexes Bona TDS documents into Azure Cognitive Search"""
    
    def __init__(self, service_name: str, admin_key: str, index_name: str = "bona-documents"):
        """Initialize the indexer with Azure Cognitive Search credentials"""
        self.service_name = service_name
        self.admin_key = admin_key
        self.index_name = index_name
        self.endpoint = f"https://{service_name}.search.windows.net"
        self.client = SearchClient(
            endpoint=self.endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(admin_key)
        )
        print(f"✅ Connected to Cognitive Search: {self.endpoint}")
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in words
            overlap: Overlap size in words between chunks
            
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def read_document(self, file_path: Path) -> Tuple[str, str]:
        """
        Read document content and extract metadata
        
        Args:
            file_path: Path to TDS file
            
        Returns:
            Tuple of (content, filename)
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return content, file_path.name
        except Exception as e:
            print(f"  ⚠️  Error reading {file_path}: {e}")
            return "", ""
    
    def index_documents(self, docs_path: str) -> Dict[str, int]:
        """
        Index all TDS files from the specified directory
        
        Args:
            docs_path: Path to directory containing TDS files
            
        Returns:
            Dictionary with indexing statistics
        """
        docs_dir = Path(docs_path)
        
        if not docs_dir.exists():
            print(f"❌ Directory not found: {docs_path}")
            return {"success": 0, "failed": 0, "total_chunks": 0}
        
        # Find all TXT files
        txt_files = list(docs_dir.glob("*.txt"))
        if not txt_files:
            print(f"⚠️  No TXT files found in {docs_path}")
            return {"success": 0, "failed": 0, "total_chunks": 0}
        
        print(f"\n📄 Found {len(txt_files)} TDS files to index")
        print("─" * 60)
        
        stats = {"success": 0, "failed": 0, "total_chunks": 0}
        all_documents = []
        doc_id = 1
        
        for file_path in txt_files:
            print(f"\n📖 Processing: {file_path.name}")
            
            # Read document
            content, filename = self.read_document(file_path)
            if not content:
                stats["failed"] += 1
                continue
            
            # Chunk the document
            chunks = self.chunk_text(content)
            print(f"   ✓ Chunked into {len(chunks)} segments")
            
            # Create search documents
            for chunk_idx, chunk in enumerate(chunks):
                doc = {
                    "id": str(doc_id),
                    "content": chunk,
                    "source": filename,
                    "chunk_index": chunk_idx,
                    "file_size": len(content),
                    "total_chunks": len(chunks)
                }
                all_documents.append(doc)
                doc_id += 1
            
            stats["success"] += 1
            stats["total_chunks"] += len(chunks)
        
        # Upload to Azure Cognitive Search
        print(f"\n⬆️  Uploading {len(all_documents)} chunks to Cognitive Search...")
        print("─" * 60)
        
        try:
            # Upload in batches to avoid size limits
            batch_size = 100
            for i in range(0, len(all_documents), batch_size):
                batch = all_documents[i:i + batch_size]
                result = self.client.upload_documents(documents=batch)
                uploaded = sum(1 for r in result if r.succeeded)
                print(f"  ✓ Batch {i//batch_size + 1}: {uploaded}/{len(batch)} chunks uploaded")
            
            print(f"\n✅ Successfully indexed {stats['total_chunks']} chunks from {stats['success']} documents")
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            stats["failed"] += stats["success"]
            stats["success"] = 0
        
        return stats

def main():
    parser = argparse.ArgumentParser(
        description="Index Bona TDS documents to Azure Cognitive Search"
    )
    parser.add_argument(
        "--service-name",
        default=os.getenv("AZURE_SEARCH_SERVICE_NAME"),
        help="Cognitive Search service name (or AZURE_SEARCH_SERVICE_NAME env var)"
    )
    parser.add_argument(
        "--admin-key",
        default=os.getenv("AZURE_SEARCH_ADMIN_KEY"),
        help="Cognitive Search admin key (or AZURE_SEARCH_ADMIN_KEY env var)"
    )
    parser.add_argument(
        "--docs-path",
        default="./ragf",
        help="Path to TDS documents directory"
    )
    parser.add_argument(
        "--index-name",
        default="bona-documents",
        help="Cognitive Search index name"
    )
    
    args = parser.parse_args()
    
    # Validate credentials
    if not args.service_name:
        print("❌ Error: --service-name required (or set AZURE_SEARCH_SERVICE_NAME)")
        sys.exit(1)
    if not args.admin_key:
        print("❌ Error: --admin-key required (or set AZURE_SEARCH_ADMIN_KEY)")
        sys.exit(1)
    
    # Initialize indexer
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   BONA TDS DOCUMENT INDEXING                                   ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    indexer = DocumentIndexer(args.service_name, args.admin_key, args.index_name)
    
    # Index documents
    stats = indexer.index_documents(args.docs_path)
    
    # Print summary
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║   INDEXING COMPLETE                                            ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"\n📊 Results:")
    print(f"  • Documents processed: {stats['success']}")
    print(f"  • Documents failed: {stats['failed']}")
    print(f"  • Total chunks indexed: {stats['total_chunks']}")
    
    if stats['success'] > 0:
        print(f"\n✅ Indexing successful!")
        print(f"   Documents are now searchable in Cognitive Search")
    else:
        print(f"\n❌ Indexing failed - no documents were indexed")
        sys.exit(1)

if __name__ == "__main__":
    main()
