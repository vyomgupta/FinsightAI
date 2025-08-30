"""
Embedding Service for FinSightAI
Supports Jina embedding model
"""
import os
import logging
from typing import List, Optional, Union, Dict, Any
import numpy as np
from pathlib import Path
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings using Jina model
    """
    
    def __init__(self, 
                 model_name: str = "jina-embeddings-v3",
                 model_type: str = "jina",
                 jina_api_key: Optional[str] = None,
                 cache_dir: Optional[str] = None):
        """
        Initialize the embedding service
        
        Args:
            model_name: Name of the embedding model to use (default: jina-embeddings-v3)
            model_type: Type of model (fixed to 'jina')
            jina_api_key: Jina API key if using Jina embeddings
            cache_dir: Directory to cache models (not used for Jina API)
        """
        self.model_name = model_name
        self.model_type = "jina" # Force model type to jina
        self.cache_dir = cache_dir or Path.home() / ".cache" / "finsight_embeddings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Set API keys
        if jina_api_key:
            self.jina_api_key = jina_api_key
        elif os.getenv("JINA_API_KEY"):
            self.jina_api_key = os.getenv("JINA_API_KEY")
        else:
            self.jina_api_key = None
        
        # Initialize the embedding model
        self.model = self._initialize_model()
        
        # Get embedding dimensions
        self.embedding_dim = self._get_embedding_dimension()
        
        logger.info(f"Embedding service initialized with {self.model_type}:{self.model_name}")
        logger.info(f"Embedding dimension: {self.embedding_dim}")
    
    def _initialize_model(self):
        """Initialize the embedding model based on type"""
        try:
            if self.model_type == "jina":
                return self._init_jina()
            else:
                raise RuntimeError("Only Jina embedding model is supported.")
        except Exception as e:
            logger.error(f"Error initializing embedding model: {e}")
            raise
    
    def _init_jina(self):
        """Initialize Jina embeddings"""
        if not self.jina_api_key:
            raise ValueError("Jina API key not provided. Set JINA_API_KEY environment variable or pass jina_api_key parameter")
        
        logger.info("Using Jina embeddings")
        return "jina"
    
    def _get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        try:
            if self.model_type == "jina":
                # Jina embeddings v3 with text-matching task are 1024 dimensions
                return 1024
            else:
                return 1024  # Default fallback for Jina
        except Exception as e:
            logger.warning(f"Could not determine embedding dimension: {e}")
            return 1024  # Default fallback
    
    def encode(self, texts: Union[str, List[str]], 
               batch_size: int = 32,
               normalize: bool = True) -> Union[List[float], List[List[float]]]:
        """
        Encode text(s) to embeddings
        
        Args:
            texts: Single text string or list of text strings
            batch_size: Batch size for processing multiple texts
            normalize: Whether to normalize embeddings to unit vectors (Jina embeddings are typically normalized by default)
        
        Returns:
            Single embedding or list of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
            single_text = True
        else:
            single_text = False
        
        try:
            if self.model_type == "jina":
                embeddings = self._encode_jina(texts)
            else:
                raise ValueError(f"Unknown model type: {self.model_type}")
            
            # Convert to list if numpy array
            if isinstance(embeddings, np.ndarray):
                embeddings = embeddings.tolist()
            
            return embeddings[0] if single_text else embeddings
            
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            raise
    
    def _encode_jina(self, texts: List[str]) -> List[List[float]]:
        """Encode texts using Jina API"""
        try:
            url = "https://api.jina.ai/v1/embeddings"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.jina_api_key}"
            }
            
            # Process texts in batches (using a reasonable default batch size)
            batch_size = 32  # Jina API can handle reasonable batch sizes
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                payload = {
                    "model": self.model_name,
                    "task": "text-matching",  # Default task for Jina v3
                    "input": batch_texts
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                batch_embeddings = [item["embedding"] for item in data["data"]]
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Jina API request error: {e}")
            raise
        except Exception as e:
            logger.error(f"Jina encoding error: {e}")
            raise
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Cosine similarity score between -1 and 1
        """
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def batch_similarity(self, query_embedding: List[float], 
                         embeddings: List[List[float]]) -> List[float]:
        """
        Calculate similarity between query embedding and multiple embeddings
        
        Args:
            query_embedding: Query embedding vector
            embeddings: List of embedding vectors
        
        Returns:
            List of similarity scores
        """
        return [self.similarity(query_embedding, emb) for emb in embeddings]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current embedding model"""
        return {
            "model_type": self.model_type,
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "cache_directory": str(self.cache_dir),
            "available_models": {
                "jina": True
            }
        }


def create_embedding_service(model_name: str = "jina-embeddings-v3",
                           model_type: str = "jina",
                           jina_api_key: Optional[str] = None,
                           cache_dir: Optional[str] = None) -> EmbeddingService:
    """
    Factory function to create an embedding service
    
    Args:
        model_name: Name of the embedding model to use
        model_type: Type of model ('jina')
        jina_api_key: Jina API key
        cache_dir: Directory to cache models
    
    Returns:
        Configured EmbeddingService instance
    """
    # Ensure cache_dir is a Path object
    if cache_dir is None:
        cache_dir = Path.home() / ".cache" / "finsight_embeddings"
    elif isinstance(cache_dir, str):
        cache_dir = Path(cache_dir)
    else:
        cache_dir = Path(cache_dir)
    
    return EmbeddingService(
        model_name=model_name,
        model_type=model_type,
        jina_api_key=jina_api_key,
        cache_dir=cache_dir
    )


if __name__ == "__main__":
    # Test the embedding service
    if os.getenv("JINA_API_KEY"):
        print("\nTesting Jina embeddings...")
        jina_service = create_embedding_service()
        
        # Test encoding
        texts = ["This is a test sentence.", "Another test sentence."]
        jina_embeddings = jina_service.encode(texts)
        print(f"Jina model info: {jina_service.get_model_info()}")
        print(f"Jina embeddings shape: {len(jina_embeddings)} x {len(jina_embeddings[0])}")
        
        jina_similarity = jina_service.similarity(jina_embeddings[0], jina_embeddings[1])
        print(f"Jina similarity between texts: {jina_similarity:.4f}")
    else:
        print("JINA_API_KEY not set. Skipping Jina embedding service test.")
