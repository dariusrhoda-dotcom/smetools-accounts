"""
RAG-based Payroll AI Assistant for South African Payroll Tax Queries
"""

from .document_processor import DocumentProcessor
from .vector_store import SimpleVectorStore
from .rag_engine import RAGEngine
from .ingestion import TaxDataIngestion, create_knowledge_base

__all__ = ['DocumentProcessor', 'SimpleVectorStore', 'RAGEngine', 'TaxDataIngestion', 'create_knowledge_base']