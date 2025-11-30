"""
Tests for the RAG Engine module.
"""

import os
import tempfile

import numpy as np
import pytest

from knowledge_server.vector_db.vector_store import VectorStore
from knowledge_server.graph_db.graph_store import GraphStore


# Skip tests if sentence-transformers model cannot be loaded (e.g., no network access)
def get_rag_engine():
    """Try to create a RAG engine, skip if model unavailable."""
    try:
        from knowledge_server.rag.rag_engine import RAGEngine
        
        with tempfile.TemporaryDirectory() as tmpdir:
            vector_store = VectorStore(dimension=384)
            db_path = os.path.join(tmpdir, "test_graph_db")
            graph_store = GraphStore(db_path)
            engine = RAGEngine(vector_store, graph_store)
            return engine, graph_store, tmpdir
    except OSError as e:
        if "huggingface" in str(e).lower() or "couldn't connect" in str(e).lower():
            pytest.skip("Cannot load embedding model (no network access)")
        raise


class TestRAGEngine:
    """Test cases for RAGEngine."""
    
    @pytest.fixture
    def rag_engine(self):
        """Create a RAG engine with temporary storage."""
        try:
            from knowledge_server.rag.rag_engine import RAGEngine
        except ImportError:
            pytest.skip("RAGEngine not available")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            vector_store = VectorStore(dimension=384)
            # Kuzu requires a path that doesn't exist yet
            db_path = os.path.join(tmpdir, "test_graph_db")
            graph_store = GraphStore(db_path)
            
            try:
                engine = RAGEngine(vector_store, graph_store)
            except OSError as e:
                if "huggingface" in str(e).lower() or "couldn't connect" in str(e).lower():
                    pytest.skip("Cannot load embedding model (no network access)")
                raise
            
            yield engine
            
            graph_store.close()
    
    def test_init(self, rag_engine):
        """Test RAGEngine initialization."""
        assert rag_engine.vector_store is not None
        assert rag_engine.graph_store is not None
        assert rag_engine.embedding_model is not None
    
    def test_embed_text(self, rag_engine):
        """Test text embedding."""
        embedding = rag_engine.embed_text("Hello world")
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == 384
    
    def test_embed_texts(self, rag_engine):
        """Test batch text embedding."""
        embeddings = rag_engine.embed_texts(["Hello", "World"])
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (2, 384)
    
    def test_add_document(self, rag_engine):
        """Test adding a document."""
        rag_engine.add_document(
            doc_id="doc1",
            title="Test Document",
            content="This is a test document about machine learning.",
        )
        
        # Verify in graph store
        doc = rag_engine.graph_store.get_document("doc1")
        assert doc is not None
        
        # Verify in vector store
        assert len(rag_engine.vector_store) > 0
    
    def test_retrieve(self, rag_engine):
        """Test document retrieval."""
        # Add documents
        rag_engine.add_document(
            doc_id="doc1",
            title="Machine Learning",
            content="Machine learning is a subset of artificial intelligence.",
        )
        rag_engine.add_document(
            doc_id="doc2",
            title="Deep Learning",
            content="Deep learning uses neural networks with many layers.",
        )
        
        # Search
        results = rag_engine.retrieve("What is AI?", top_k=2)
        
        assert len(results) == 2
        assert all("score" in r for r in results)
    
    def test_get_context(self, rag_engine):
        """Test getting context for generation."""
        rag_engine.add_document(
            doc_id="doc1",
            title="Test",
            content="This is test content for context generation.",
        )
        
        context = rag_engine.get_context("test content", top_k=1)
        
        assert isinstance(context, str)
        assert len(context) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
