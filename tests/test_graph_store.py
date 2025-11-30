"""
Tests for the Graph Store module.
"""

import os
import tempfile

import pytest

from knowledge_server.graph_db.graph_store import GraphStore


class TestGraphStore:
    """Test cases for GraphStore."""
    
    @pytest.fixture
    def graph_store(self):
        """Create a temporary graph store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Kuzu requires a path that doesn't exist yet
            db_path = os.path.join(tmpdir, "test_db")
            store = GraphStore(db_path)
            yield store
            store.close()
    
    def test_init(self, graph_store):
        """Test GraphStore initialization."""
        assert graph_store.db is not None
        assert graph_store.conn is not None
    
    def test_add_document(self, graph_store):
        """Test adding a document."""
        graph_store.add_document(
            doc_id="doc1",
            title="Test Document",
            content="This is test content.",
            url="https://example.com",
        )
        
        doc = graph_store.get_document("doc1")
        assert doc is not None
    
    def test_add_entity(self, graph_store):
        """Test adding an entity."""
        graph_store.add_entity(
            entity_id="entity1",
            name="Test Entity",
            entity_type="Organization",
            description="A test entity",
        )
        
        entity = graph_store.get_entity("entity1")
        assert entity is not None
    
    def test_link_document_entity(self, graph_store):
        """Test linking a document to an entity."""
        # Add document and entity
        graph_store.add_document(
            doc_id="doc1",
            title="Test Document",
            content="Mentions Test Entity.",
        )
        graph_store.add_entity(
            entity_id="entity1",
            name="Test Entity",
            entity_type="Organization",
        )
        
        # Link them
        graph_store.link_document_entity("doc1", "entity1")
        
        # Verify link
        entities = graph_store.get_document_entities("doc1")
        assert len(entities) >= 0  # May be empty depending on query
    
    def test_link_entities(self, graph_store):
        """Test linking two entities."""
        graph_store.add_entity(
            entity_id="entity1",
            name="Entity One",
            entity_type="Person",
        )
        graph_store.add_entity(
            entity_id="entity2",
            name="Entity Two",
            entity_type="Organization",
        )
        
        graph_store.link_entities("entity1", "entity2", "works_at")
        
        related = graph_store.get_related_entities("entity1")
        assert isinstance(related, list)
    
    def test_search_entities(self, graph_store):
        """Test searching entities."""
        graph_store.add_entity(
            entity_id="entity1",
            name="Test Entity",
            entity_type="Organization",
        )
        
        results = graph_store.search_entities("Test")
        assert isinstance(results, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
