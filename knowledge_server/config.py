"""
Configuration settings for the Knowledge Server.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database paths
    data_dir: str = Field(default="./data", description="Base directory for data storage")
    vector_db_path: Optional[str] = Field(default=None, description="Vector database path")
    graph_db_path: Optional[str] = Field(default=None, description="Graph database path")
    
    # Vector store settings
    vector_dimension: int = Field(default=384, description="Vector embedding dimension")
    vector_metric: str = Field(default="cos", description="Distance metric (cos, l2, ip)")
    
    # Embedding model
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence transformer model name"
    )
    
    # Reranker settings
    use_reranker: bool = Field(
        default=False,
        description="Whether to use reranking by default"
    )
    reranker_model: str = Field(
        default="ms-marco-MiniLM-L-6-v2",
        description="Reranker model name (see docs for available models)"
    )
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Scraping settings
    scrape_delay: float = Field(default=1.0, description="Delay between requests")
    scrape_concurrent: int = Field(default=4, description="Concurrent requests")
    
    class Config:
        env_prefix = "KNOWLEDGE_"
        env_file = ".env"
    
    def get_vector_db_path(self) -> str:
        """Get the vector database path."""
        if self.vector_db_path:
            return self.vector_db_path
        return os.path.join(self.data_dir, "vector_store")
    
    def get_graph_db_path(self) -> str:
        """Get the graph database path."""
        if self.graph_db_path:
            return self.graph_db_path
        return os.path.join(self.data_dir, "graph_store")
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.get_vector_db_path()).parent.mkdir(parents=True, exist_ok=True)
        Path(self.get_graph_db_path()).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
