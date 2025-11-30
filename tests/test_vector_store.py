"""
Tests for the Vector Store module.
"""

import os
import tempfile

import numpy as np
import pytest

from knowledge_server.vector_db.vector_store import VectorStore


class TestVectorStore:
    """Test cases for VectorStore."""
    
    def test_init(self):
        """Test VectorStore initialization."""
        store = VectorStore(dimension=128)
        assert store.dimension == 128
        assert store.metric == "cos"
        assert len(store) == 0
    
    def test_add_vectors(self):
        """Test adding vectors."""
        store = VectorStore(dimension=128)
        
        vectors = np.random.rand(5, 128).astype(np.float32)
        texts = [f"Text {i}" for i in range(5)]
        
        ids = store.add(vectors, texts)
        
        assert len(ids) == 5
        assert len(store) == 5
    
    def test_search(self):
        """Test vector search."""
        store = VectorStore(dimension=128)
        
        # Add some vectors
        vectors = np.random.rand(10, 128).astype(np.float32)
        texts = [f"Text {i}" for i in range(10)]
        store.add(vectors, texts)
        
        # Search
        query = vectors[0]  # Use first vector as query
        results = store.search(query, top_k=3)
        
        assert len(results) == 3
        # First result should be the same vector
        assert results[0][2] == "Text 0"
    
    def test_save_load(self):
        """Test saving and loading index."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_index.usearch")
            
            # Create and save
            store = VectorStore(dimension=128, db_path=db_path)
            vectors = np.random.rand(5, 128).astype(np.float32)
            texts = [f"Text {i}" for i in range(5)]
            store.add(vectors, texts)
            store.save()
            
            # Load in new instance
            store2 = VectorStore(dimension=128, db_path=db_path)
            store2.load(db_path)
            
            assert len(store2) == 5
    
    def test_delete(self):
        """Test deleting vectors."""
        store = VectorStore(dimension=128)
        
        vectors = np.random.rand(5, 128).astype(np.float32)
        texts = [f"Text {i}" for i in range(5)]
        ids = store.add(vectors, texts)
        
        # Delete first vector
        store.delete([ids[0]])
        
        # Text mapping should be removed
        assert ids[0] not in store._id_to_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
