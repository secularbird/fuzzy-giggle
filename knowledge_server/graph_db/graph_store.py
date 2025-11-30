"""
Graph Database Client using Kùzu DB for knowledge graph storage.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import kuzu


class GraphStore:
    """Graph store implementation using Kùzu DB."""
    
    def __init__(self, db_path: str):
        """
        Initialize the graph store.
        
        Args:
            db_path: Path to the Kùzu database directory.
        """
        self.db_path = db_path
        # Kuzu requires the parent directory to exist but not the db path itself
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(self.db)
        
        self._initialize_schema()
    
    def _initialize_schema(self) -> None:
        """Initialize the knowledge graph schema."""
        # Create Document node table
        try:
            self.conn.execute("""
                CREATE NODE TABLE Document(
                    id STRING PRIMARY KEY,
                    title STRING,
                    content STRING,
                    url STRING
                )
            """)
        except Exception:
            pass
        
        # Create Entity node table
        try:
            self.conn.execute("""
                CREATE NODE TABLE Entity(
                    id STRING PRIMARY KEY,
                    name STRING,
                    entity_type STRING,
                    description STRING
                )
            """)
        except Exception:
            pass
        
        # Create relationships
        try:
            self.conn.execute("""
                CREATE REL TABLE MENTIONS(
                    FROM Document TO Entity
                )
            """)
        except Exception:
            pass
        
        try:
            self.conn.execute("""
                CREATE REL TABLE RELATED_TO(
                    FROM Entity TO Entity,
                    relation_type STRING
                )
            """)
        except Exception:
            pass
    
    def _result_to_dict(self, result: kuzu.QueryResult) -> List[Dict[str, Any]]:
        """Convert Kuzu query result to list of dictionaries."""
        columns = result.get_column_names()
        rows = []
        while result.has_next():
            row_values = result.get_next()
            rows.append(dict(zip(columns, row_values)))
        return rows
    
    def add_document(
        self,
        doc_id: str,
        title: str,
        content: str,
        url: Optional[str] = None,
    ) -> None:
        """
        Add a document to the graph.
        
        Args:
            doc_id: Unique document ID.
            title: Document title.
            content: Document content.
            url: Optional source URL.
        """
        # Check if document exists
        result = self.conn.execute(
            "MATCH (d:Document {id: $id}) RETURN d.id",
            {"id": doc_id}
        )
        
        if result.has_next():
            # Update existing document
            self.conn.execute(
                """
                MATCH (d:Document {id: $id})
                SET d.title = $title, d.content = $content, d.url = $url
                """,
                {"id": doc_id, "title": title, "content": content, "url": url or ""},
            )
        else:
            # Create new document
            self.conn.execute(
                """
                CREATE (:Document {id: $id, title: $title, content: $content, url: $url})
                """,
                {"id": doc_id, "title": title, "content": content, "url": url or ""},
            )
    
    def add_entity(
        self,
        entity_id: str,
        name: str,
        entity_type: str,
        description: Optional[str] = None,
    ) -> None:
        """
        Add an entity to the graph.
        
        Args:
            entity_id: Unique entity ID.
            name: Entity name.
            entity_type: Type of entity (e.g., 'Person', 'Organization').
            description: Optional entity description.
        """
        # Check if entity exists
        result = self.conn.execute(
            "MATCH (e:Entity {id: $id}) RETURN e.id",
            {"id": entity_id}
        )
        
        if result.has_next():
            # Update existing entity
            self.conn.execute(
                """
                MATCH (e:Entity {id: $id})
                SET e.name = $name, e.entity_type = $entity_type, e.description = $description
                """,
                {"id": entity_id, "name": name, "entity_type": entity_type, "description": description or ""},
            )
        else:
            # Create new entity
            self.conn.execute(
                """
                CREATE (:Entity {id: $id, name: $name, entity_type: $entity_type, description: $description})
                """,
                {"id": entity_id, "name": name, "entity_type": entity_type, "description": description or ""},
            )
    
    def link_document_entity(self, doc_id: str, entity_id: str) -> None:
        """
        Create a MENTIONS relationship between a document and an entity.
        
        Args:
            doc_id: Document ID.
            entity_id: Entity ID.
        """
        # Check if relationship already exists
        result = self.conn.execute(
            """
            MATCH (d:Document {id: $doc_id})-[r:MENTIONS]->(e:Entity {id: $entity_id})
            RETURN r
            """,
            {"doc_id": doc_id, "entity_id": entity_id}
        )
        
        if not result.has_next():
            self.conn.execute(
                """
                MATCH (d:Document {id: $doc_id}), (e:Entity {id: $entity_id})
                CREATE (d)-[:MENTIONS]->(e)
                """,
                {"doc_id": doc_id, "entity_id": entity_id},
            )
    
    def link_entities(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
    ) -> None:
        """
        Create a RELATED_TO relationship between two entities.
        
        Args:
            source_id: Source entity ID.
            target_id: Target entity ID.
            relation_type: Type of relationship.
        """
        # Check if relationship already exists
        result = self.conn.execute(
            """
            MATCH (s:Entity {id: $source_id})-[r:RELATED_TO]->(t:Entity {id: $target_id})
            RETURN r
            """,
            {"source_id": source_id, "target_id": target_id}
        )
        
        if not result.has_next():
            self.conn.execute(
                """
                MATCH (s:Entity {id: $source_id}), (t:Entity {id: $target_id})
                CREATE (s)-[:RELATED_TO {relation_type: $relation_type}]->(t)
                """,
                {"source_id": source_id, "target_id": target_id, "relation_type": relation_type},
            )
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.
        
        Args:
            doc_id: Document ID.
            
        Returns:
            Document data or None if not found.
        """
        result = self.conn.execute(
            "MATCH (d:Document {id: $id}) RETURN d.id, d.title, d.content, d.url",
            {"id": doc_id},
        )
        
        rows = self._result_to_dict(result)
        return rows[0] if rows else None
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an entity by ID.
        
        Args:
            entity_id: Entity ID.
            
        Returns:
            Entity data or None if not found.
        """
        result = self.conn.execute(
            "MATCH (e:Entity {id: $id}) RETURN e.id, e.name, e.entity_type, e.description",
            {"id": entity_id},
        )
        
        rows = self._result_to_dict(result)
        return rows[0] if rows else None
    
    def get_document_entities(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Get all entities mentioned in a document.
        
        Args:
            doc_id: Document ID.
            
        Returns:
            List of entity data.
        """
        result = self.conn.execute(
            """
            MATCH (d:Document {id: $id})-[:MENTIONS]->(e:Entity)
            RETURN e.id, e.name, e.entity_type, e.description
            """,
            {"id": doc_id},
        )
        
        return self._result_to_dict(result)
    
    def get_related_entities(
        self,
        entity_id: str,
        relation_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get entities related to a given entity.
        
        Args:
            entity_id: Entity ID.
            relation_type: Optional filter by relation type.
            
        Returns:
            List of related entities with relation info.
        """
        if relation_type:
            result = self.conn.execute(
                """
                MATCH (s:Entity {id: $id})-[r:RELATED_TO]->(t:Entity)
                WHERE r.relation_type = $rel_type
                RETURN t.id, t.name, t.entity_type, t.description, r.relation_type
                """,
                {"id": entity_id, "rel_type": relation_type},
            )
        else:
            result = self.conn.execute(
                """
                MATCH (s:Entity {id: $id})-[r:RELATED_TO]->(t:Entity)
                RETURN t.id, t.name, t.entity_type, t.description, r.relation_type
                """,
                {"id": entity_id},
            )
        
        return self._result_to_dict(result)
    
    def search_entities(
        self,
        name_pattern: str,
        entity_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search entities by name pattern.
        
        Args:
            name_pattern: Pattern to search for in entity names.
            entity_type: Optional filter by entity type.
            
        Returns:
            List of matching entities.
        """
        if entity_type:
            result = self.conn.execute(
                """
                MATCH (e:Entity)
                WHERE contains(e.name, $pattern) AND e.entity_type = $type
                RETURN e.id, e.name, e.entity_type, e.description
                """,
                {"pattern": name_pattern, "type": entity_type},
            )
        else:
            result = self.conn.execute(
                """
                MATCH (e:Entity)
                WHERE contains(e.name, $pattern)
                RETURN e.id, e.name, e.entity_type, e.description
                """,
                {"pattern": name_pattern},
            )
        
        return self._result_to_dict(result)
    
    def close(self) -> None:
        """Close the database connection."""
        # Kùzu handles cleanup automatically
        pass
