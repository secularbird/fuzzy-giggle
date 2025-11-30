"""
Reranker Module for improving retrieval quality.
Uses cross-encoder models to rerank retrieved documents.
"""

from typing import Any, Dict, List, Optional, Tuple

from sentence_transformers import CrossEncoder


# Available reranker models with their characteristics
RERANKER_MODELS = {
    "ms-marco-MiniLM-L-6-v2": {
        "name": "cross-encoder/ms-marco-MiniLM-L-6-v2",
        "description": "Fast and efficient, good for general use (22M params)",
        "max_length": 512,
    },
    "ms-marco-MiniLM-L-12-v2": {
        "name": "cross-encoder/ms-marco-MiniLM-L-12-v2",
        "description": "Better accuracy than L-6, still fast (33M params)",
        "max_length": 512,
    },
    "bge-reranker-base": {
        "name": "BAAI/bge-reranker-base",
        "description": "Good balance of performance and accuracy (278M params)",
        "max_length": 512,
    },
    "bge-reranker-large": {
        "name": "BAAI/bge-reranker-large",
        "description": "High accuracy, suitable for quality-critical applications (560M params)",
        "max_length": 512,
    },
    "bge-reranker-v2-m3": {
        "name": "BAAI/bge-reranker-v2-m3",
        "description": "Multilingual support, good for Chinese and other languages",
        "max_length": 8192,
    },
}

# Default model - good balance of speed and accuracy
DEFAULT_RERANKER_MODEL = "ms-marco-MiniLM-L-6-v2"


class Reranker:
    """
    Reranker for improving retrieval quality using cross-encoder models.
    
    Cross-encoders process query-document pairs together, providing more
    accurate relevance scores than bi-encoder similarity search alone.
    """
    
    def __init__(
        self,
        model_name: str = DEFAULT_RERANKER_MODEL,
        device: Optional[str] = None,
    ):
        """
        Initialize the reranker.
        
        Args:
            model_name: Name of the reranker model (see RERANKER_MODELS for options).
            device: Device to run the model on ('cpu', 'cuda', etc.). Auto-detected if None.
        """
        if model_name in RERANKER_MODELS:
            self.model_info = RERANKER_MODELS[model_name]
            full_model_name = self.model_info["name"]
        else:
            # Allow using custom model names directly
            self.model_info = {
                "name": model_name,
                "description": "Custom model",
                "max_length": 512,
            }
            full_model_name = model_name
        
        self.model_name = model_name
        self.model = CrossEncoder(full_model_name, device=device)
        self.max_length = self.model_info.get("max_length", 512)
    
    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None,
    ) -> List[Tuple[int, float, str]]:
        """
        Rerank documents based on relevance to the query.
        
        Args:
            query: The search query.
            documents: List of document texts to rerank.
            top_k: Number of top documents to return. Returns all if None.
            
        Returns:
            List of tuples (original_index, score, document_text) sorted by score descending.
        """
        if not documents:
            return []
        
        # Create query-document pairs
        pairs = [[query, doc] for doc in documents]
        
        # Get relevance scores from cross-encoder
        scores = self.model.predict(pairs)
        
        # Combine with original indices and sort by score
        results = [
            (idx, float(score), doc) 
            for idx, (score, doc) in enumerate(zip(scores, documents))
        ]
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k if specified
        if top_k is not None and top_k < len(results):
            results = results[:top_k]
        
        return results
    
    def rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        content_key: str = "content",
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Rerank retrieval results and update their scores.
        
        Args:
            query: The search query.
            results: List of result dictionaries from retrieval.
            content_key: Key to access document content in results.
            top_k: Number of top results to return. Returns all if None.
            
        Returns:
            Reranked results with updated scores.
        """
        if not results:
            return []
        
        # Extract documents
        documents = [r.get(content_key, "") for r in results]
        
        # Rerank
        reranked = self.rerank(query, documents, top_k=None)
        
        # Build reranked results
        reranked_results = []
        for original_idx, new_score, _ in reranked:
            result = results[original_idx].copy()
            result["original_score"] = result.get("score", 0)
            result["score"] = new_score
            result["reranked"] = True
            reranked_results.append(result)
        
        # Return top_k if specified
        if top_k is not None and top_k < len(reranked_results):
            reranked_results = reranked_results[:top_k]
        
        return reranked_results
    
    @staticmethod
    def list_available_models() -> Dict[str, Dict[str, str]]:
        """
        List all available reranker models.
        
        Returns:
            Dictionary of model names to their information.
        """
        return RERANKER_MODELS.copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information.
        """
        return {
            "model_name": self.model_name,
            **self.model_info,
        }
