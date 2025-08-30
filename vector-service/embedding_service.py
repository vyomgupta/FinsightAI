"""
Embedding Service for FinSightAI
Supports multiple embedding models with fallback options
"""
import os
import logging
from typing import List, Optional, Union, Dict, Any
import numpy as np
from pathlib import Path
import requests

# Try to import different embedding libraries
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings using various models
    """
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 model_type: str = "sentence_transformers",
                 openai_api_key: Optional[str] = None,
                 jina_api_key: Optional[str] = None,
                 cache_dir: Optional[str] = None):
        """
        Initialize the embedding service
        
        Args:
            model_name: Name of the embedding model to use
            model_type: Type of model ('sentence_transformers', 'openai', 'langchain', 'jina')
            openai_api_key: OpenAI API key if using OpenAI embeddings
            jina_api_key: Jina API key if using Jina embeddings
            cache_dir: Directory to cache models
        """
        self.model_name = model_name
        self.model_type = model_type
        self.cache_dir = cache_dir or Path.home() / ".cache" / "finsight_embeddings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Set API keys
        if openai_api_key:
            openai.api_key = openai_api_key
        elif os.getenv("OPENAI_API_KEY"):
            openai.api_key = os.getenv("OPENAI_API_KEY")
            
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
        
        logger.info(f"Embedding service initialized with {model_type}:{model_name}")
        logger.info(f"Embedding dimension: {self.embedding_dim}")
    
    def _initialize_model(self):
        """Initialize the embedding model based on type"""
        try:
            if self.model_type == "sentence_transformers" and SENTENCE_TRANSFORMERS_AVAILABLE:
                return self._init_sentence_transformers()
            elif self.model_type == "openai" and OPENAI_AVAILABLE:
                return self._init_openai()
            elif self.model_type == "langchain" and LANGCHAIN_AVAILABLE:
                return self._init_langchain()
            elif self.model_type == "jina":
                return self._init_jina()
            else:
                # Fallback to sentence_transformers if available
                if SENTENCE_TRANSFORMERS_AVAILABLE:
                    logger.warning(f"Requested model type {self.model_type} not available, falling back to sentence_transformers")
                    self.model_type = "sentence_transformers"
                    return self._init_sentence_transformers()
                else:
                    raise RuntimeError("No embedding models available. Please install sentence-transformers, openai, or langchain")
        except Exception as e:
            logger.error(f"Error initializing embedding model: {e}")
            raise
    
    def _init_sentence_transformers(self):
        """Initialize SentenceTransformers model"""
        try:
            model = SentenceTransformer(self.model_name, cache_folder=str(self.cache_dir))
            logger.info(f"Loaded SentenceTransformers model: {self.model_name}")
            return model
        except Exception as e:
            logger.error(f"Error loading SentenceTransformers model: {e}")
            raise
    
    def _init_openai(self):
        """Initialize OpenAI embeddings"""
        if not openai.api_key:
            raise ValueError("OpenAI API key not provided")
        
        logger.info("Using OpenAI embeddings")
        return "openai"
    
    def _init_langchain(self):
        """Initialize LangChain embeddings"""
        if self.model_name.startswith("text-embedding-"):
            # OpenAI model
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OpenAI API key not provided for LangChain OpenAI embeddings")
            model = OpenAIEmbeddings(model=self.model_name)
        else:
            # HuggingFace model
            model = HuggingFaceEmbeddings(
                model_name=self.model_name,
                cache_folder=str(self.cache_dir)
            )
        
        logger.info(f"Loaded LangChain model: {self.model_name}")
        return model
    
    def _init_jina(self):
        """Initialize Jina embeddings"""
        if not self.jina_api_key:
            raise ValueError("Jina API key not provided. Set JINA_API_KEY environment variable or pass jina_api_key parameter")
        
        logger.info("Using Jina embeddings")
        return "jina"
    
    def _get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        try:
            if self.model_type == "sentence_transformers":
                # Get dimension from model
                test_embedding = self.model.encode("test")
                return len(test_embedding)
            elif self.model_type == "openai":
                # OpenAI embeddings are typically 1536 dimensions
                return 1536
            elif self.model_type == "langchain":
                # Get dimension from model
                test_embedding = self.model.embed_query("test")
                return len(test_embedding)
            elif self.model_type == "jina":
                # Jina embeddings v3 with text-matching task are 1024 dimensions
                return 1024
            else:
                return 384  # Default fallback
        except Exception as e:
            logger.warning(f"Could not determine embedding dimension: {e}")
            return 384  # Default fallback
    
    def encode(self, texts: Union[str, List[str]], 
               batch_size: int = 32,
               normalize: bool = True) -> Union[List[float], List[List[float]]]:
        """
        Encode text(s) to embeddings
        
        Args:
            texts: Single text string or list of text strings
            batch_size: Batch size for processing multiple texts
            normalize: Whether to normalize embeddings to unit vectors
        
        Returns:
            Single embedding or list of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
            single_text = True
        else:
            single_text = False
        
        try:
            if self.model_type == "sentence_transformers":
                embeddings = self.model.encode(
                    texts, 
                    batch_size=batch_size,
                    normalize_embeddings=normalize
                )
            elif self.model_type == "openai":
                embeddings = self._encode_openai(texts)
            elif self.model_type == "langchain":
                embeddings = self._encode_langchain(texts)
            elif self.model_type == "jina":
                embeddings = self._encode_jina(texts)
            else:
                raise ValueError(f"Unknown model type: {self.model_type}")
            
            # Convert to list if numpy array
            if isinstance(embeddings, np.ndarray):
                embeddings = embeddings.tolist()
            
            # Normalize if requested and not already normalized
            if normalize and self.model_type not in ["sentence_transformers", "jina"]:
                embeddings = self._normalize_embeddings(embeddings)
            
            return embeddings[0] if single_text else embeddings
            
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            raise
    
    def _encode_openai(self, texts: List[str]) -> List[List[float]]:
        """Encode texts using OpenAI API"""
        try:
            response = openai.Embedding.create(
                input=texts,
                model="text-embedding-ada-002"
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"OpenAI encoding error: {e}")
            raise
    
    def _encode_langchain(self, texts: List[str]) -> List[List[float]]:
        """Encode texts using LangChain"""
        try:
            if len(texts) == 1:
                return [self.model.embed_query(texts[0])]
            else:
                return self.model.embed_documents(texts)
        except Exception as e:
            logger.error(f"LangChain encoding error: {e}")
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
    
    def _normalize_embeddings(self, embeddings: List[List[float]]) -> List[List[float]]:
        """Normalize embeddings to unit vectors"""
        normalized = []
        for embedding in embeddings:
            norm = np.linalg.norm(embedding)
            if norm > 0:
                normalized.append([x / norm for x in embedding])
            else:
                normalized.append(embedding)
        return normalized
    
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
                "sentence_transformers": SENTENCE_TRANSFORMERS_AVAILABLE,
                "openai": OPENAI_AVAILABLE,
                "langchain": LANGCHAIN_AVAILABLE,
                "jina": True  # Always available since it uses HTTP API
            }
        }


# Factory function for easy model creation
def create_embedding_service(model_name: str = "all-MiniLM-L6-v2",
                           model_type: str = "sentence_transformers",
                           **kwargs) -> EmbeddingService:
    """
    Factory function to create an embedding service
    
    Args:
        model_name: Name of the embedding model
        model_type: Type of model to use
        **kwargs: Additional arguments for EmbeddingService
    
    Returns:
        Configured EmbeddingService instance
    """
    return EmbeddingService(model_name=model_name, model_type=model_type, **kwargs)


# Pre-configured models
def get_default_embedding_service() -> EmbeddingService:
    """Get a default embedding service with recommended settings"""
    return create_embedding_service(
        model_name="all-MiniLM-L6-v2",
        model_type="sentence_transformers"
    )


def get_jina_embedding_service(api_key: Optional[str] = None) -> EmbeddingService:
    """Get a Jina embeddings service with recommended settings"""
    return create_embedding_service(
        model_name="jina-embeddings-v3",
        model_type="jina",
        jina_api_key=api_key
    )


if __name__ == "__main__":
    # Test the embedding service
    service = get_default_embedding_service()
    
    # Test encoding
    texts = ["This is a test sentence.", "Another test sentence."]
    embeddings = service.encode(texts)
    
    print(f"Model info: {service.get_model_info()}")
    print(f"Embeddings shape: {len(embeddings)} x {len(embeddings[0])}")
    
    # Test similarity
    similarity = service.similarity(embeddings[0], embeddings[1])
    print(f"Similarity between texts: {similarity:.4f}")
    
    # Test Jina service if API key is available
    if os.getenv("JINA_API_KEY"):
        print("\nTesting Jina embeddings...")
        jina_service = get_jina_embedding_service()
        jina_embeddings = jina_service.encode(texts)
        print(f"Jina model info: {jina_service.get_model_info()}")
        print(f"Jina embeddings shape: {len(jina_embeddings)} x {len(jina_embeddings[0])}")
        
        jina_similarity = jina_service.similarity(jina_embeddings[0], jina_embeddings[1])
        print(f"Jina similarity between texts: {jina_similarity:.4f}")
