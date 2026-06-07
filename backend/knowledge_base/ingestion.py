"""
Tax Data Ingestion System for monthly updates.
Handles loading initial tax data and scheduled updates.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import urllib.request
import urllib.error

from .document_processor import DocumentProcessor
from .vector_store import SimpleVectorStore
from .rag_engine import RAGEngine


class TaxDataIngestion:
    """
    Manages ingestion of SARS tax data into the RAG knowledge base.
    Handles both initial data loading and monthly updates.
    """
    
    SARS_UPDATE_URLS = [
        "https://www.sars.gov.za/wp-content/uploads/Occs/2024/Tables-PAYE-2024-2025.pdf",
        "https://www.sars.gov.za/wp-content/uploads/Occs/2024/ETI-Table-2024-2025.pdf",
    ]
    
    def __init__(
        self, 
        vector_store: SimpleVectorStore,
        document_processor: Optional[DocumentProcessor] = None
    ):
        """
        Initialize the ingestion system.
        
        Args:
            vector_store: Vector store to populate with tax data
            document_processor: Optional document processor (creates default if None)
        """
        self.vector_store = vector_store
        self.document_processor = document_processor or DocumentProcessor()
        self.rag_engine = RAGEngine(vector_store)
        self._last_update: Optional[datetime] = None
        self._update_log: List[Dict[str, Any]] = []
    
    def load_initial_tax_data(self, data_directory: str) -> Dict[str, Any]:
        """
        Load initial tax data from JSON files.
        
        Args:
            data_directory: Path to directory containing tax JSON files
            
        Returns:
            Summary of loaded data
        """
        path = Path(data_directory)
        
        if not path.exists():
            return {
                'success': False,
                'error': f"Directory not found: {data_directory}",
                'documents_loaded': 0,
                'chunks_created': 0
            }
        
        # Process all JSON files
        chunks = self.document_processor.process_directory(str(path))
        
        if not chunks:
            return {
                'success': False,
                'error': "No tax data found in files",
                'documents_loaded': 0,
                'chunks_created': 0
            }
        
        # Convert chunks to documents format for vector store
        documents = [
            {
                'content': chunk.content,
                'metadata': {
                    **chunk.metadata,
                    'source_file': 'initial_load',
                    'loaded_at': datetime.now().isoformat()
                }
            }
            for chunk in chunks
        ]
        
        # Add to vector store
        doc_ids = self.vector_store.add_documents(documents)
        
        self._last_update = datetime.now()
        self._update_log.append({
            'timestamp': self._last_update.isoformat(),
            'action': 'initial_load',
            'source': data_directory,
            'documents_loaded': len(doc_ids),
            'chunks_created': len(chunks)
        })
        
        return {
            'success': True,
            'documents_loaded': len(doc_ids),
            'chunks_created': len(chunks),
            'tax_years': self.rag_engine.get_tax_years(),
            'categories': self.rag_engine.get_categories()
        }
    
    def check_for_updates(self) -> Dict[str, Any]:
        """
        Check for available SARS tax updates.
        In production, this would scrape the SARS website or check RSS feeds.
        
        Returns:
            Status of available updates
        """
        # Simulated check - in production would actually fetch from SARS
        available_updates = []
        
        current_years = set(self.rag_engine.get_tax_years())
        
        # Check for new tax year (simulated for March each year)
        now = datetime.now()
        if now.month == 3 and str(now.year + 1) not in current_years:
            available_updates.append({
                'type': 'new_tax_year',
                'year': now.year + 1,
                'description': f'New tax year {now.year + 1}/{now.year + 2} begins March 1'
            })
        
        # Check for mid-year adjustments (typically February)
        if now.month == 2:
            available_updates.append({
                'type': 'mid_year_adjustment',
                'description': 'Check for annual tax table updates'
            })
        
        return {
            'checked_at': datetime.now().isoformat(),
            'available_updates': available_updates,
            'last_update': self._last_update.isoformat() if self._last_update else None,
            'update_log': self._update_log[-5:]  # Last 5 updates
        }
    
    def simulate_monthly_update(self, tax_year: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate ingesting a monthly update.
        In production, this would parse data fetched from SARS website.
        
        Args:
            tax_year: The tax year this data applies to
            data: Tax data dictionary
            
        Returns:
            Summary of update
        """
        # Create chunks from new data
        temp_file = f"/tmp/tax_update_{tax_year}.json"
        with open(temp_file, 'w') as f:
            json.dump({**data, 'tax_year': tax_year}, f)
        
        try:
            chunks = self.document_processor.process_json_tax_file(temp_file)
            
            documents = [
                {
                    'content': chunk.content,
                    'metadata': {
                        **chunk.metadata,
                        'source_file': f'update_{tax_year}',
                        'loaded_at': datetime.now().isoformat()
                    }
                }
                for chunk in chunks
            ]
            
            doc_ids = self.vector_store.add_documents(documents)
            
            self._last_update = datetime.now()
            self._update_log.append({
                'timestamp': self._last_update.isoformat(),
                'action': 'monthly_update',
                'tax_year': tax_year,
                'documents_loaded': len(doc_ids),
                'chunks_created': len(chunks)
            })
            
            return {
                'success': True,
                'tax_year': tax_year,
                'documents_loaded': len(doc_ids),
                'chunks_created': len(chunks)
            }
        finally:
            # Clean up temp file
            Path(temp_file).unlink(missing_ok=True)
    
    def get_update_status(self) -> Dict[str, Any]:
        """Get the current status of the knowledge base and update history."""
        return {
            'knowledge_base': {
                'total_documents': self.vector_store.count(),
                'tax_years': self.rag_engine.get_tax_years(),
                'categories': self.rag_engine.get_categories()
            },
            'last_update': self._last_update.isoformat() if self._last_update else None,
            'update_history': self._update_log[-10:]  # Last 10 updates
        }
    
    def export_knowledge_base(self, export_path: str) -> Dict[str, Any]:
        """
        Export the knowledge base to a file for backup.
        
        Args:
            export_path: Path to export file
            
        Returns:
            Export status
        """
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'documents': [
                {
                    'id': doc.id,
                    'content': doc.content,
                    'metadata': doc.metadata
                }
                for doc in self.vector_store.documents.values()
            ],
            'update_log': self._update_log
        }
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return {
            'success': True,
            'export_path': export_path,
            'documents_exported': len(export_data['documents'])
        }
    
    def import_knowledge_base(self, import_path: str) -> Dict[str, Any]:
        """
        Import a knowledge base from a backup file.
        
        Args:
            import_path: Path to import file
            
        Returns:
            Import status
        """
        with open(import_path, 'r') as f:
            import_data = json.load(f)
        
        documents = [
            {
                'content': doc['content'],
                'metadata': doc['metadata']
            }
            for doc in import_data.get('documents', [])
        ]
        
        if documents:
            doc_ids = self.vector_store.add_documents(documents)
        else:
            doc_ids = []
        
        self._update_log.extend(import_data.get('update_log', []))
        
        return {
            'success': True,
            'documents_imported': len(doc_ids),
            'updates_restored': len(import_data.get('update_log', []))
        }


def create_knowledge_base(data_directory: str) -> RAGEngine:
    """
    Factory function to create and initialize a complete knowledge base.
    
    Args:
        data_directory: Path to directory with tax JSON files
        
    Returns:
        Initialized RAGEngine ready for queries
    """
    vector_store = SimpleVectorStore()
    ingestion = TaxDataIngestion(vector_store)
    
    result = ingestion.load_initial_tax_data(data_directory)
    
    if not result.get('success'):
        raise ValueError(f"Failed to load initial tax data: {result.get('error')}")
    
    return ingestion.rag_engine