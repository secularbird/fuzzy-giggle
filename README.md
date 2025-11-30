# Knowledge Server

A RAG (Retrieval-Augmented Generation) based knowledge server built with Python, combining vector database (usearch), graph database (Kùzu DB), and web scraping (Scrapy) capabilities.

## Features

- **Vector Database (usearch)**: Fast similarity search for document embeddings
- **Graph Database (Kùzu DB)**: Knowledge graph storage for entities and relationships
- **RAG Engine**: Combines vector and graph-based retrieval for enhanced context
- **Web Scraping (Scrapy)**: Automated content extraction from web pages
- **REST API (FastAPI)**: Easy-to-use HTTP endpoints for all operations

## Installation

```bash
# Clone the repository
git clone https://github.com/secularbird/fuzzy-giggle.git
cd fuzzy-giggle

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Start the API Server

```bash
# Run the server
python -m knowledge_server serve

# Or with custom host/port
python -m knowledge_server serve --host 0.0.0.0 --port 8000
```

### Add Documents

```bash
# Via CLI
python -m knowledge_server add \
    --id doc1 \
    --title "Introduction to AI" \
    --content "Artificial intelligence is transforming industries..."

# Via API
curl -X POST http://localhost:8000/documents \
    -H "Content-Type: application/json" \
    -d '{"doc_id": "doc1", "title": "AI Intro", "content": "..."}'
```

### Search the Knowledge Base

```bash
# Via CLI
python -m knowledge_server search "artificial intelligence"

# Via API
curl -X POST http://localhost:8000/search \
    -H "Content-Type: application/json" \
    -d '{"query": "artificial intelligence", "top_k": 5}'
```

### Scrape Web Content

```bash
# Via CLI
python -m knowledge_server scrape https://example.com -o output.json

# Via API
curl -X POST http://localhost:8000/scrape \
    -H "Content-Type: application/json" \
    -d '{"urls": ["https://example.com"], "add_to_knowledge_base": true}'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/documents` | POST | Add a document |
| `/documents/{doc_id}` | GET | Get document by ID |
| `/entities` | POST | Add an entity |
| `/entities/{entity_id}` | GET | Get entity by ID |
| `/entities/link` | POST | Link two entities |
| `/entities/{entity_id}/related` | GET | Get related entities |
| `/search` | POST | Search knowledge base |
| `/context` | POST | Get context for generation |
| `/scrape` | POST | Scrape URLs |

## Configuration

Configuration can be set via environment variables with the `KNOWLEDGE_` prefix:

```bash
export KNOWLEDGE_DATA_DIR=./data
export KNOWLEDGE_VECTOR_DIMENSION=384
export KNOWLEDGE_EMBEDDING_MODEL=all-MiniLM-L6-v2
export KNOWLEDGE_HOST=0.0.0.0
export KNOWLEDGE_PORT=8000
```

Or create a `.env` file:

```env
KNOWLEDGE_DATA_DIR=./data
KNOWLEDGE_EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## Project Structure

```
knowledge_server/
├── __init__.py          # Package initialization
├── __main__.py          # CLI entry point
├── config.py            # Configuration settings
├── api/
│   ├── __init__.py
│   └── server.py        # FastAPI server
├── vector_db/
│   ├── __init__.py
│   └── vector_store.py  # usearch vector database
├── graph_db/
│   ├── __init__.py
│   └── graph_store.py   # Kùzu graph database
├── rag/
│   ├── __init__.py
│   └── rag_engine.py    # RAG engine
└── scrapy_server/
    ├── __init__.py
    ├── spider.py        # Scrapy spiders
    └── runner.py        # Scrapy runner
```

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Knowledge Server API                     │
│                        (FastAPI)                            │
├─────────────────────────────────────────────────────────────┤
│                       RAG Engine                            │
│   ┌─────────────────────┐    ┌─────────────────────────┐   │
│   │   Vector Store      │    │    Graph Store          │   │
│   │   (usearch)         │    │    (Kùzu DB)            │   │
│   │   - Embeddings      │    │    - Documents          │   │
│   │   - Similarity      │    │    - Entities           │   │
│   │     Search          │    │    - Relationships      │   │
│   └─────────────────────┘    └─────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Scrapy Server                            │
│   - Web Content Scraping                                    │
│   - Automated Knowledge Ingestion                           │
└─────────────────────────────────────────────────────────────┘
```

## License

MIT License

---

## 文档 | Documentation

- [用户手册 (User Manual)](docs/USER_MANUAL.md) - 详细的使用指南
- [架构设计 (Architecture)](docs/ARCHITECTURE.md) - 系统架构和技术设计
