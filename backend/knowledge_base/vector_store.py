"""
Simple In-Memory Vector Store for RAG system.
Provides vector storage and similarity search without external dependencies.
"""

import uuid
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class Document:
    """Represents a document in the knowledge base."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class SimpleVectorStore:
    """
    A simple in-memory vector store using TF-IDF-like embeddings.
    Supports basic semantic search through cosine similarity.
    """
    
    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self._vocabulary: Dict[str, int] = {}
        self._doc_count: int = 0
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Add documents to the store.
        
        Args:
            documents: List of dicts with 'content' and 'metadata' keys
            
        Returns:
            List of created document IDs
        """
        ids = []
        for doc in documents:
            doc_id = str(uuid.uuid4())
            content = doc['content']
            metadata = doc.get('metadata', {})
            
            # Create document
            document = Document(
                id=doc_id,
                content=content,
                metadata=metadata
            )
            
            # Compute embedding
            document.embedding = self._compute_embedding(content)
            
            self.documents[doc_id] = document
            self._update_vocabulary(content)
            ids.append(doc_id)
            self._doc_count += 1
        
        return ids
    
    def _compute_embedding(self, text: str) -> List[float]:
        """
        Compute a simple embedding using word frequency.
        In production, this would use sentence transformers or similar.
        """
        # Tokenize and normalize
        words = re.findall(r'\w+', text.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Create vector based on vocabulary
        vector = []
        for term, idx in self._vocabulary.items():
            vector.append(word_freq.get(term, 0))
        
        # Normalize
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 0:
            vector = [v / magnitude for v in vector]
        
        return vector
    
    def _update_vocabulary(self, text: str):
        """Update vocabulary with words from text."""
        words = set(re.findall(r'\w+', text.lower()))
        for word in words:
            if word not in self._vocabulary:
                self._vocabulary[word] = len(self._vocabulary)
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 5, 
        threshold: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Find top k most similar documents to query.
        
        Args:
            query: Search query text
            k: Number of results to return
            threshold: Minimum similarity score
            
        Returns:
            List of document dicts with content and metadata
        """
        if not self.documents:
            return []
        
        # Compute query embedding
        query_embedding = self._compute_embedding(query)
        
        # Calculate similarities
        results = []
        for doc_id, doc in self.documents.items():
            if doc.embedding is None:
                continue
            
            similarity = self._cosine_similarity(query_embedding, doc.embedding)
            if similarity >= threshold:
                results.append({
                    'id': doc_id,
                    'content': doc.content,
                    'metadata': doc.metadata,
                    'similarity': similarity
                })
        
        # Sort by similarity and return top k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            # Pad shorter vector
            max_len = max(len(vec1), len(vec2))
            vec1 = vec1 + [0] * (max_len - len(vec1))
            vec2 = vec2 + [0] * (max_len - len(vec2))
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        return dot_product
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by ID."""
        doc = self.documents.get(doc_id)
        if doc:
            return {
                'id': doc.id,
                'content': doc.content,
                'metadata': doc.metadata
            }
        return None
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            return True
        return False
    
    def count(self) -> int:
        """Return total number of documents."""
        return len(self.documents)
    
    def clear(self):
        """Clear all documents."""
        self.documents.clear()
        self._vocabulary.clear()
        self._doc_count = 0