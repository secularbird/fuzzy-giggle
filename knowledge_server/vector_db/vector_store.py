"""
Vector Database Client using usearch for similarity search.
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np
from usearch.index import Index


class VectorStore:
    """Vector store implementation using usearch."""
    
    def __init__(
        self,
        dimension: int = 384,
        metric: str = "cos",
        db_path: Optional[str] = None,
    ):
        """
        Initialize the vector store.
        
        Args:
            dimension: The dimension of the vectors (default: 384 for all-MiniLM-L6-v2).
            metric: The distance metric to use ('cos', 'l2', 'ip').
            db_path: Optional path to persist the index.
        """
        self.dimension = dimension
        self.metric = metric
        self.db_path = db_path
        self.index = Index(ndim=dimension, metric=metric)
        self._id_to_text: dict = {}
        self._current_id: int = 0
        
        if db_path and os.path.exists(db_path):
            self.load(db_path)
    
    def add(
        self,
        vectors: Union[np.ndarray, List[List[float]]],
        texts: Optional[List[str]] = None,
        ids: Optional[List[int]] = None,
    ) -> List[int]:
        """
        Add vectors to the index.
        
        Args:
            vectors: The vectors to add.
            texts: Optional text content associated with each vector.
            ids: Optional IDs for the vectors.
            
        Returns:
            List of IDs assigned to the vectors.
        """
        vectors = np.array(vectors, dtype=np.float32)
        
        if ids is None:
            ids = list(range(self._current_id, self._current_id + len(vectors)))
            self._current_id += len(vectors)
        
        self.index.add(ids, vectors)
        
        if texts:
            for i, text in zip(ids, texts):
                self._id_to_text[i] = text
        
        return ids
    
    def search(
        self,
        query_vector: Union[np.ndarray, List[float]],
        top_k: int = 10,
    ) -> List[Tuple[int, float, Optional[str]]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: The query vector.
            top_k: Number of results to return.
            
        Returns:
            List of tuples (id, score, text).
        """
        query_vector = np.array(query_vector, dtype=np.float32)
        
        matches = self.index.search(query_vector, top_k)
        
        results = []
        for key, distance in zip(matches.keys, matches.distances):
            text = self._id_to_text.get(int(key))
            results.append((int(key), float(distance), text))
        
        return results
    
    def delete(self, ids: List[int]) -> None:
        """
        Delete vectors by their IDs.
        
        Args:
            ids: List of IDs to delete.
        """
        for id_ in ids:
            if id_ in self._id_to_text:
                del self._id_to_text[id_]
    
    def save(self, path: Optional[str] = None) -> None:
        """
        Save the index to disk.
        
        Args:
            path: Path to save the index. Uses db_path if not specified.
        """
        save_path = path or self.db_path
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            self.index.save(save_path)
            
            # Save text mapping separately
            text_path = f"{save_path}.texts.npy"
            np.save(text_path, self._id_to_text, allow_pickle=True)
    
    def load(self, path: str) -> None:
        """
        Load the index from disk.
        
        Args:
            path: Path to load the index from.
        """
        self.index.load(path)
        
        text_path = f"{path}.texts.npy"
        if os.path.exists(text_path):
            self._id_to_text = np.load(text_path, allow_pickle=True).item()
    
    def __len__(self) -> int:
        """Return the number of vectors in the index."""
        return len(self.index)
