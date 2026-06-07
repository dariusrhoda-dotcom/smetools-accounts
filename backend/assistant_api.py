"""
API views for the Payroll AI Assistant.
"""

import json
from pathlib import Path
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView

from knowledge_base import (
    SimpleVectorStore,
    DocumentProcessor,
    TaxDataIngestion
)


# Global RAG engine instance (initialized on first request)
_rag_engine = None
_ingestion = None


def get_rag_engine():
    """Get or initialize the RAG engine singleton."""
    global _rag_engine, _ingestion
    
    if _rag_engine is None:
        # Initialize vector store and ingestion
        vector_store = SimpleVectorStore()
        _ingestion = TaxDataIngestion(vector_store)
        
        # Load initial tax data
        tax_data_dir = '/home/team/shared/tax_data'
        if Path(tax_data_dir).exists():
            _ingestion.load_initial_tax_data(tax_data_dir)
        
        _rag_engine = _ingestion.rag_engine
    
    return _rag_engine


class AssistantQueryView(APIView):
    """
    API endpoint for querying the payroll assistant.
    
    POST /api/assistant/query/
    {
        "question": "What is the tax threshold for someone under 65?"
    }
    """
    
    def post(self, request):
        question = request.data.get('question', '')
        
        if not question:
            return Response(
                {'error': 'Question is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rag_engine = get_rag_engine()
        result = rag_engine.query(question)
        
        return Response(result)


class AssistantCategoriesView(APIView):
    """
    API endpoint to list available tax categories.
    
    GET /api/assistant/categories/
    """
    
    def get(self, request):
        rag_engine = get_rag_engine()
        categories = rag_engine.get_categories()
        return Response({'categories': categories})


class AssistantTaxYearsView(APIView):
    """
    API endpoint to list available tax years.
    
    GET /api/assistant/tax-years/
    """
    
    def get(self, request):
        rag_engine = get_rag_engine()
        tax_years = rag_engine.get_tax_years()
        return Response({'tax_years': tax_years})


class AssistantKnowledgeBaseStatusView(APIView):
    """
    API endpoint to check knowledge base status.
    
    GET /api/assistant/status/
    """
    
    def get(self, request):
        global _ingestion
        
        if _ingestion is None:
            get_rag_engine()
        
        status = _ingestion.get_update_status()
        return Response(status)


class AssistantUpdatesView(APIView):
    """
    API endpoint to check for SARS updates.
    
    GET /api/assistant/updates/
    """
    
    def get(self, request):
        global _ingestion
        
        if _ingestion is None:
            get_rag_engine()
        
        updates = _ingestion.check_for_updates()
        return Response(updates)


@api_view(['POST'])
def query_with_filter(request):
    """
    Query the assistant with optional category filter.
    
    POST /api/assistant/query-filtered/
    {
        "question": "How is UIF calculated?",
        "category": "uif"
    }
    """
    question = request.data.get('question', '')
    category = request.data.get('category')
    
    if not question:
        return Response(
            {'error': 'Question is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    rag_engine = get_rag_engine()
    result = rag_engine.query(question, filter_category=category)
    
    return Response(result)


@api_view(['POST'])
def simulate_update(request):
    """
    Simulate ingesting a tax data update.
    
    POST /api/assistant/simulate-update/
    {
        "tax_year": "2025",
        "data": { ... tax data ... }
    }
    """
    global _ingestion, _rag_engine
    
    tax_year = request.data.get('tax_year')
    data = request.data.get('data', {})
    
    if not tax_year:
        return Response(
            {'error': 'Tax year is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if _ingestion is None:
        get_rag_engine()
    
    result = _ingestion.simulate_monthly_update(tax_year, data)
    
    # Reset RAG engine to pick up new data
    _rag_engine = None
    get_rag_engine()
    
    return Response(result)


@api_view(['POST'])
def export_knowledge_base(request):
    """
    Export the knowledge base to a file.
    
    POST /api/assistant/export/
    {
        "path": "/path/to/export.json"
    }
    """
    global _ingestion
    
    export_path = request.data.get('path', '/tmp/knowledge_base_export.json')
    
    if _ingestion is None:
        get_rag_engine()
    
    result = _ingestion.export_knowledge_base(export_path)
    return Response(result)


@api_view(['POST'])
def import_knowledge_base(request):
    """
    Import the knowledge base from a file.
    
    POST /api/assistant/import/
    {
        "path": "/path/to/import.json"
    }
    """
    global _ingestion, _rag_engine
    
    import_path = request.data.get('path')
    
    if not import_path:
        return Response(
            {'error': 'Path is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if _ingestion is None:
        get_rag_engine()
    
    result = _ingestion.import_knowledge_base(import_path)
    
    # Reset RAG engine to pick up new data
    _rag_engine = None
    get_rag_engine()
    
    return Response(result)