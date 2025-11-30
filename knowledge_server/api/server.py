"""
FastAPI server for the Knowledge Server.
"""

import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from knowledge_server.vector_db.vector_store import VectorStore
from knowledge_server.graph_db.graph_store import GraphStore
from knowledge_server.rag.rag_engine import RAGEngine


# Request/Response models
class DocumentRequest(BaseModel):
    """Request model for adding a document."""
    
    doc_id: str = Field(..., description="Unique document ID")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    url: Optional[str] = Field(None, description="Source URL")
    entities: Optional[List[Dict[str, str]]] = Field(
        None, description="List of entities with 'id', 'name', 'type'"
    )


class EntityRequest(BaseModel):
    """Request model for adding an entity."""
    
    entity_id: str = Field(..., description="Unique entity ID")
    name: str = Field(..., description="Entity name")
    entity_type: str = Field(..., description="Entity type")
    description: Optional[str] = Field(None, description="Entity description")


class EntityLinkRequest(BaseModel):
    """Request model for linking entities."""
    
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    relation_type: str = Field(..., description="Type of relationship")


class SearchRequest(BaseModel):
    """Request model for search."""
    
    query: str = Field(..., description="Search query")
    top_k: int = Field(5, description="Number of results to return")
    include_graph: bool = Field(True, description="Include graph context")
    entity_name: Optional[str] = Field(None, description="Entity name to search")
    use_reranker: Optional[bool] = Field(None, description="Use reranking (overrides default)")


class ScrapeRequest(BaseModel):
    """Request model for scraping."""
    
    urls: List[str] = Field(..., description="URLs to scrape")
    add_to_knowledge_base: bool = Field(
        True, description="Add scraped content to knowledge base"
    )


class RetrievalResult(BaseModel):
    """Response model for retrieval results."""
    
    id: int
    score: float
    content: Optional[str]
    entities: Optional[List[Dict[str, Any]]] = None
    original_score: Optional[float] = None
    reranked: Optional[bool] = None


class SearchResponse(BaseModel):
    """Response model for search."""
    
    results: List[RetrievalResult]
    graph_results: Optional[Dict[str, Any]] = None


# Global state
rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """Get the RAG engine instance."""
    global rag_engine
    if rag_engine is None:
        raise HTTPException(status_code=500, detail="RAG engine not initialized")
    return rag_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    global rag_engine
    
    # Initialize components on startup
    db_path = os.environ.get("KNOWLEDGE_DB_PATH", "./data")
    vector_path = os.path.join(db_path, "vector_store")
    graph_path = os.path.join(db_path, "graph_store")
    
    os.makedirs(db_path, exist_ok=True)
    
    vector_store = VectorStore(dimension=384, db_path=vector_path)
    graph_store = GraphStore(graph_path)
    
    # Get reranker settings from environment
    use_reranker = os.environ.get("KNOWLEDGE_USE_RERANKER", "false").lower() == "true"
    reranker_model = os.environ.get("KNOWLEDGE_RERANKER_MODEL", "ms-marco-MiniLM-L-6-v2")
    
    rag_engine = RAGEngine(
        vector_store, 
        graph_store,
        use_reranker=use_reranker,
        reranker_model=reranker_model if use_reranker else None,
    )
    
    yield
    
    # Cleanup on shutdown
    if rag_engine:
        rag_engine.vector_store.save()
        rag_engine.graph_store.close()


# Create FastAPI app
app = FastAPI(
    title="Knowledge Server",
    description="RAG-based knowledge server with vector and graph databases",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/documents", response_model=Dict[str, str])
async def add_document(request: DocumentRequest) -> Dict[str, str]:
    """Add a document to the knowledge base."""
    engine = get_rag_engine()
    
    engine.add_document(
        doc_id=request.doc_id,
        title=request.title,
        content=request.content,
        url=request.url,
        entities=request.entities,
    )
    
    return {"status": "success", "doc_id": request.doc_id}


@app.get("/documents/{doc_id}")
async def get_document(doc_id: str) -> Dict[str, Any]:
    """Get a document by ID."""
    engine = get_rag_engine()
    
    doc = engine.graph_store.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return doc


@app.post("/entities", response_model=Dict[str, str])
async def add_entity(request: EntityRequest) -> Dict[str, str]:
    """Add an entity to the knowledge graph."""
    engine = get_rag_engine()
    
    engine.graph_store.add_entity(
        entity_id=request.entity_id,
        name=request.name,
        entity_type=request.entity_type,
        description=request.description,
    )
    
    return {"status": "success", "entity_id": request.entity_id}


@app.get("/entities/{entity_id}")
async def get_entity(entity_id: str) -> Dict[str, Any]:
    """Get an entity by ID."""
    engine = get_rag_engine()
    
    entity = engine.graph_store.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return entity


@app.post("/entities/link", response_model=Dict[str, str])
async def link_entities(request: EntityLinkRequest) -> Dict[str, str]:
    """Link two entities with a relationship."""
    engine = get_rag_engine()
    
    engine.graph_store.link_entities(
        source_id=request.source_id,
        target_id=request.target_id,
        relation_type=request.relation_type,
    )
    
    return {"status": "success"}


@app.get("/entities/{entity_id}/related")
async def get_related_entities(
    entity_id: str, relation_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get entities related to a given entity."""
    engine = get_rag_engine()
    
    return engine.graph_store.get_related_entities(entity_id, relation_type)


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    """Search the knowledge base."""
    engine = get_rag_engine()
    
    if request.entity_name:
        combined = engine.retrieve_with_graph(
            query=request.query,
            entity_name=request.entity_name,
            top_k=request.top_k,
        )
        
        results = [
            RetrievalResult(
                id=r["id"],
                score=r["score"],
                content=r.get("content"),
            )
            for r in combined["vector_results"]
        ]
        
        return SearchResponse(
            results=results,
            graph_results=combined["graph_results"],
        )
    else:
        vector_results = engine.retrieve(
            query=request.query,
            top_k=request.top_k,
            include_graph_context=request.include_graph,
            use_reranker=request.use_reranker,
        )
        
        results = [
            RetrievalResult(
                id=r["id"],
                score=r["score"],
                content=r.get("content"),
                entities=r.get("entities"),
                original_score=r.get("original_score"),
                reranked=r.get("reranked"),
            )
            for r in vector_results
        ]
        
        return SearchResponse(results=results)


@app.post("/context")
async def get_context(
    query: str, top_k: int = 3, max_tokens: int = 2000
) -> Dict[str, str]:
    """Get context for a query (for use in generation)."""
    engine = get_rag_engine()
    
    context = engine.get_context(query, top_k, max_tokens)
    
    return {"context": context}


@app.post("/scrape")
async def scrape_urls(request: ScrapeRequest) -> Dict[str, Any]:
    """Scrape URLs and optionally add to knowledge base."""
    try:
        from knowledge_server.scrapy_server.runner import AsyncScrapyRunner
    except ImportError:
        raise HTTPException(
            status_code=500, detail="Scraping dependencies not installed"
        )
    
    runner = AsyncScrapyRunner()
    results = []
    
    for url in request.urls:
        try:
            scraped = await runner.scrape_url(url)
            results.append(scraped)
            
            if request.add_to_knowledge_base:
                engine = get_rag_engine()
                doc_id = f"scraped_{hash(url) % (10**9)}"
                engine.add_document(
                    doc_id=doc_id,
                    title=scraped["title"],
                    content=scraped["content"],
                    url=url,
                )
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    
    return {"scraped": results}


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the knowledge server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


@app.get("/rerankers")
async def list_rerankers() -> Dict[str, Any]:
    """List available reranker models and current configuration."""
    from knowledge_server.rag.reranker import Reranker, RERANKER_MODELS
    
    engine = get_rag_engine()
    
    current_model = None
    if engine.reranker:
        current_model = engine.reranker.get_model_info()
    
    return {
        "available_models": RERANKER_MODELS,
        "current_model": current_model,
        "reranking_enabled": engine.use_reranker,
    }


if __name__ == "__main__":
    run_server()
