"""
Test script for the Payroll AI Assistant RAG system.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, '/home/team/shared/backend')

from knowledge_base import (
    SimpleVectorStore,
    DocumentProcessor,
    TaxDataIngestion,
    create_knowledge_base
)


def test_vector_store():
    """Test basic vector store operations."""
    print("\n=== Testing Vector Store ===")
    
    store = SimpleVectorStore()
    
    # Add sample documents
    docs = [
        {
            'content': 'South African income tax brackets for 2025: 18% for income above R237,100',
            'metadata': {'category': 'tax_brackets', 'tax_year': '2025'}
        },
        {
            'content': 'UIF employee contribution rate is 1% of earnings up to a cap of R17,711.58',
            'metadata': {'category': 'uif', 'tax_year': '2025'}
        }
    ]
    
    ids = store.add_documents(docs)
    print(f"Added {len(ids)} documents, IDs: {ids}")
    print(f"Total documents: {store.count()}")
    
    # Search
    results = store.similarity_search('tax brackets', k=2)
    print(f"\nSearch results for 'tax brackets':")
    for r in results:
        print(f"  - {r['content'][:60]}... (score: {r['similarity']:.3f})")
    
    print("✓ Vector store test passed")


def test_document_processor():
    """Test document processing."""
    print("\n=== Testing Document Processor ===")
    
    processor = DocumentProcessor()
    
    # Process the 2025 tax data
    chunks = processor.process_json_tax_file('/home/team/shared/tax_data/2025.json')
    
    print(f"Processed {len(chunks)} chunks from 2025.json:")
    for chunk in chunks:
        print(f"  - [{chunk.metadata['category']}] {chunk.content[:50]}...")
    
    print("✓ Document processor test passed")


def test_ingestion():
    """Test full ingestion pipeline."""
    print("\n=== Testing Tax Data Ingestion ===")
    
    store = SimpleVectorStore()
    ingestion = TaxDataIngestion(store)
    
    result = ingestion.load_initial_tax_data('/home/team/shared/tax_data')
    
    print(f"Load result: {result}")
    print(f"Documents in store: {store.count()}")
    print(f"Tax years: {ingestion.rag_engine.get_tax_years()}")
    print(f"Categories: {ingestion.rag_engine.get_categories()}")
    
    print("✓ Ingestion test passed")


def test_rag_queries():
    """Test RAG query functionality."""
    print("\n=== Testing RAG Queries ===")
    
    # Create knowledge base
    rag_engine = create_knowledge_base('/home/team/shared/tax_data')
    
    # Test queries
    queries = [
        "What are the income tax brackets for 2025?",
        "How is UIF calculated?",
        "What is the tax threshold for someone under 65?",
        "How much is the primary rebate?",
        "Tell me about ETI for young workers",
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = rag_engine.query(query)
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Sources used: {result['num_sources_used']}")
    
    print("✓ RAG queries test passed")


def test_api_endpoints():
    """Test API endpoints (requires Django server)."""
    print("\n=== Testing API Endpoints ===")
    print("Note: Start Django server with 'python manage.py runserver' first")
    print("Then test with curl:")
    print("  curl -X POST http://localhost:8000/api/assistant/query/ -d '{\"question\": \"What is UIF?\"}'")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("PAYROLL AI ASSISTANT - RAG SYSTEM TESTS")
    print("=" * 60)
    
    try:
        test_vector_store()
        test_document_processor()
        test_ingestion()
        test_rag_queries()
        test_api_endpoints()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
    except Exception as e:
        print(f"\n\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)