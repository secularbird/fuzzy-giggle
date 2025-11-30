"""
Tests for the API Server module.
"""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient


def create_test_client():
    """Create a test client, skip if embedding model unavailable."""
    # Set up test environment
    os.environ["KNOWLEDGE_DB_PATH"] = tempfile.mkdtemp()
    
    try:
        from knowledge_server.api.server import app
        return TestClient(app)
    except OSError as e:
        if "huggingface" in str(e).lower() or "couldn't connect" in str(e).lower():
            pytest.skip("Cannot load embedding model (no network access)")
        raise


class TestAPIServer:
    """Test cases for the API server."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return create_test_client()
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_add_document(self, client):
        """Test adding a document."""
        response = client.post(
            "/documents",
            json={
                "doc_id": "test_doc_1",
                "title": "Test Document",
                "content": "This is a test document.",
            },
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
    
    def test_add_entity(self, client):
        """Test adding an entity."""
        response = client.post(
            "/entities",
            json={
                "entity_id": "test_entity_1",
                "name": "Test Entity",
                "entity_type": "Organization",
            },
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
    
    def test_search(self, client):
        """Test search endpoint."""
        # First add a document
        client.post(
            "/documents",
            json={
                "doc_id": "search_test_doc",
                "title": "Search Test",
                "content": "This document is about machine learning and AI.",
            },
        )
        
        # Then search
        response = client.post(
            "/search",
            json={"query": "machine learning", "top_k": 5},
        )
        
        assert response.status_code == 200
        assert "results" in response.json()
    
    def test_get_context(self, client):
        """Test context endpoint."""
        # Add a document first
        client.post(
            "/documents",
            json={
                "doc_id": "context_test_doc",
                "title": "Context Test",
                "content": "Context for testing the get context endpoint.",
            },
        )
        
        response = client.post(
            "/context",
            params={"query": "context test", "top_k": 1},
        )
        
        assert response.status_code == 200
        assert "context" in response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
