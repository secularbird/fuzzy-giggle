"""
RAG (Retrieval-Augmented Generation) Engine.
Combines vector search with graph-based knowledge retrieval.
"""

from typing import Any, Dict, List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from knowledge_server.vector_db.vector_store import VectorStore
from knowledge_server.graph_db.graph_store import GraphStore
from knowledge_server.rag.reranker import Reranker, DEFAULT_RERANKER_MODEL


class RAGEngine:
    """RAG engine that combines vector and graph-based retrieval."""
    
    def __init__(
        self,
        vector_store: VectorStore,
        graph_store: GraphStore,
        embedding_model: str = "all-MiniLM-L6-v2",
        reranker_model: Optional[str] = None,
        use_reranker: bool = False,
    ):
        """
        Initialize the RAG engine.
        
        Args:
            vector_store: VectorStore instance for similarity search.
            graph_store: GraphStore instance for knowledge graph queries.
            embedding_model: Name of the sentence transformer model.
            reranker_model: Name of the reranker model (see Reranker.list_available_models()).
            use_reranker: Whether to use reranking by default.
        """
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.embedding_model = SentenceTransformer(embedding_model)
        self.use_reranker = use_reranker
        self.reranker: Optional[Reranker] = None
        
        # Initialize reranker if requested
        if use_reranker or reranker_model:
            self.reranker = Reranker(
                model_name=reranker_model or DEFAULT_RERANKER_MODEL
            )
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        
        Args:
            text: Input text to embed.
            
        Returns:
            Embedding vector as numpy array.
        """
        return self.embedding_model.encode(text, convert_to_numpy=True)
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts.
            
        Returns:
            Array of embedding vectors.
        """
        return self.embedding_model.encode(texts, convert_to_numpy=True)
    
    def add_document(
        self,
        doc_id: str,
        title: str,
        content: str,
        url: Optional[str] = None,
        entities: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """
        Add a document to both vector and graph stores.
        
        Args:
            doc_id: Unique document ID.
            title: Document title.
            content: Document content.
            url: Optional source URL.
            entities: Optional list of entities with 'id', 'name', 'type'.
        """
        # Add to graph store
        self.graph_store.add_document(doc_id, title, content, url)
        
        # Generate embedding and add to vector store
        embedding = self.embed_text(content)
        int_id = hash(doc_id) % (10**9)
        self.vector_store.add(
            vectors=[embedding],
            texts=[content],
            ids=[int_id],
        )
        
        # Add entities and link them to the document
        if entities:
            for entity in entities:
                self.graph_store.add_entity(
                    entity_id=entity["id"],
                    name=entity["name"],
                    entity_type=entity.get("type", "Unknown"),
                    description=entity.get("description"),
                )
                self.graph_store.link_document_entity(doc_id, entity["id"])
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        include_graph_context: bool = True,
        use_reranker: Optional[bool] = None,
        rerank_top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query.
            top_k: Number of results to return.
            include_graph_context: Whether to include related entities.
            use_reranker: Whether to use reranking. Defaults to self.use_reranker.
            rerank_top_k: Number of candidates to fetch for reranking (default: top_k * 3).
            
        Returns:
            List of retrieval results with content and metadata.
        """
        # Determine if we should use reranking
        should_rerank = use_reranker if use_reranker is not None else self.use_reranker
        should_rerank = should_rerank and self.reranker is not None
        
        # If reranking, fetch more candidates
        fetch_k = top_k
        if should_rerank:
            fetch_k = rerank_top_k or (top_k * 3)
        
        # Vector similarity search
        query_embedding = self.embed_text(query)
        vector_results = self.vector_store.search(query_embedding, fetch_k)
        
        results = []
        for id_, score, text in vector_results:
            result = {
                "id": id_,
                "score": 1 - score,  # Convert distance to similarity
                "content": text,
            }
            
            if include_graph_context:
                # Try to find related entities from graph
                # Note: We'd need a mapping from vector ID to doc_id
                result["entities"] = []
            
            results.append(result)
        
        # Apply reranking if enabled
        if should_rerank and results:
            results = self.reranker.rerank_results(query, results, top_k=top_k)
        
        return results
    
    def retrieve_with_graph(
        self,
        query: str,
        entity_name: Optional[str] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Retrieve information combining vector search and graph traversal.
        
        Args:
            query: Search query.
            entity_name: Optional entity name to search for.
            top_k: Number of vector results to return.
            
        Returns:
            Combined retrieval results.
        """
        # Vector search
        vector_results = self.retrieve(query, top_k, include_graph_context=False)
        
        # Graph search
        graph_results = {}
        if entity_name:
            entities = self.graph_store.search_entities(entity_name)
            graph_results["entities"] = entities
            
            # Get related entities for each found entity
            for entity in entities:
                if "e.id" in entity:
                    related = self.graph_store.get_related_entities(entity["e.id"])
                    entity["related_entities"] = related
        
        return {
            "vector_results": vector_results,
            "graph_results": graph_results,
        }
    
    def get_context(
        self,
        query: str,
        top_k: int = 3,
        max_tokens: int = 2000,
    ) -> str:
        """
        Get context for a query to be used in generation.
        
        Args:
            query: Search query.
            top_k: Number of documents to retrieve.
            max_tokens: Approximate maximum tokens in context.
            
        Returns:
            Concatenated context string.
        """
        results = self.retrieve(query, top_k)
        
        context_parts = []
        total_chars = 0
        char_limit = max_tokens * 4  # Rough approximation
        
        for result in results:
            content = result.get("content", "")
            if content and total_chars + len(content) <= char_limit:
                context_parts.append(content)
                total_chars += len(content)
            elif content:
                # Truncate if needed
                remaining = char_limit - total_chars
                if remaining > 100:
                    context_parts.append(content[:remaining])
                break
        
        return "\n\n---\n\n".join(context_parts)
