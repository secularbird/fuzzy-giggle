#!/usr/bin/env python
"""
Main entry point for the Knowledge Server.
"""

import argparse
import sys

from knowledge_server.config import settings


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Knowledge Server - RAG-based knowledge management"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Server command
    server_parser = subparsers.add_parser("serve", help="Run the API server")
    server_parser.add_argument(
        "--host", default=settings.host, help="Server host"
    )
    server_parser.add_argument(
        "--port", type=int, default=settings.port, help="Server port"
    )
    
    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape URLs")
    scrape_parser.add_argument(
        "urls", nargs="+", help="URLs to scrape"
    )
    scrape_parser.add_argument(
        "--output", "-o", help="Output file path"
    )
    scrape_parser.add_argument(
        "--follow-links", action="store_true", help="Follow links on pages"
    )
    
    # Add document command
    add_parser = subparsers.add_parser("add", help="Add a document")
    add_parser.add_argument("--id", required=True, help="Document ID")
    add_parser.add_argument("--title", required=True, help="Document title")
    add_parser.add_argument("--content", required=True, help="Document content")
    add_parser.add_argument("--url", help="Source URL")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search knowledge base")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--top-k", type=int, default=5, help="Number of results"
    )
    
    args = parser.parse_args()
    
    if args.command == "serve":
        from knowledge_server.api.server import run_server
        settings.ensure_directories()
        run_server(host=args.host, port=args.port)
        return 0
    
    elif args.command == "scrape":
        from knowledge_server.scrapy_server.runner import ScrapyRunner
        
        runner = ScrapyRunner()
        results = runner.scrape_urls(args.urls, follow_links=args.follow_links)
        
        if args.output:
            import json
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"Saved {len(results)} results to {args.output}")
        else:
            for result in results:
                print(f"URL: {result.get('url')}")
                print(f"Title: {result.get('title')}")
                print(f"Content: {result.get('content', '')[:200]}...")
                print("-" * 50)
        
        return 0
    
    elif args.command == "add":
        from knowledge_server.vector_db.vector_store import VectorStore
        from knowledge_server.graph_db.graph_store import GraphStore
        from knowledge_server.rag.rag_engine import RAGEngine
        
        settings.ensure_directories()
        
        vector_store = VectorStore(
            dimension=settings.vector_dimension,
            db_path=settings.get_vector_db_path(),
        )
        graph_store = GraphStore(settings.get_graph_db_path())
        engine = RAGEngine(vector_store, graph_store, settings.embedding_model)
        
        engine.add_document(
            doc_id=args.id,
            title=args.title,
            content=args.content,
            url=args.url,
        )
        
        vector_store.save()
        print(f"Added document: {args.id}")
        
        return 0
    
    elif args.command == "search":
        from knowledge_server.vector_db.vector_store import VectorStore
        from knowledge_server.graph_db.graph_store import GraphStore
        from knowledge_server.rag.rag_engine import RAGEngine
        
        settings.ensure_directories()
        
        vector_store = VectorStore(
            dimension=settings.vector_dimension,
            db_path=settings.get_vector_db_path(),
        )
        graph_store = GraphStore(settings.get_graph_db_path())
        engine = RAGEngine(vector_store, graph_store, settings.embedding_model)
        
        results = engine.retrieve(args.query, args.top_k)
        
        print(f"Search results for: {args.query}")
        print("=" * 50)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. Score: {result['score']:.4f}")
            if result.get("content"):
                print(f"   Content: {result['content'][:200]}...")
            print()
        
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
