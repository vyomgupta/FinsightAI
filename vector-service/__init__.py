"""
Vector Service Package for FinSightAI
"""

__version__ = "1.0.0"
__author__ = "FinSightAI Team"

# Import key services for easy access
from .embedding_service import EmbeddingService, create_embedding_service
from .chroma_service import ChromaService, create_chroma_service
from .vector_service_manager import VectorServiceManager, create_vector_service_manager

__all__ = [
    'EmbeddingService',
    'create_embedding_service',
    'ChromaService', 
    'create_chroma_service',
    'VectorServiceManager',
    'create_vector_service_manager'
]
