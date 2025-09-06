"""
RAG (Retrieval-Augmented Generation) Service for FinSightAI
Combines vector search with LLM generation for intelligent insights
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import json

# Import vector services
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'vector-service'))

from vector_service_manager import VectorServiceManager, create_vector_service_manager
from search_service import SearchResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetrievalResult:
    """
    Represents a retrieval result with context and metadata
    """
    
    def __init__(self, 
                 search_results: List[SearchResult],
                 query: str,
                 retrieval_method: str = "hybrid",
                 total_retrieved: int = 0):
        """
        Initialize retrieval result
        
        Args:
            search_results: List of search results from vector database
            query: Original query
            retrieval_method: Method used for retrieval
            total_retrieved: Total number of documents retrieved
        """
        self.search_results = search_results
        self.query = query
        self.retrieval_method = retrieval_method
        self.total_retrieved = total_retrieved
        self.retrieved_at = datetime.now().isoformat()
    
    def get_context_text(self, max_length: int = 4000) -> str:
        """
        Get concatenated context text from all retrieved documents
        
        Args:
            max_length: Maximum length of context text
        
        Returns:
            Concatenated context text
        """
        context_parts = []
        current_length = 0
        
        for result in self.search_results:
            text = result.document.text
            if current_length + len(text) > max_length:
                # Truncate if adding this would exceed max length
                remaining_length = max_length - current_length
                if remaining_length > 100:  # Only add if we have reasonable space
                    text = text[:remaining_length - 3] + "..."
                    context_parts.append(text)
                break
            
            context_parts.append(text)
            current_length += len(text)
        
        return "\n\n".join(context_parts)
    
    def get_source_metadata(self) -> List[Dict[str, Any]]:
        """Get metadata from all source documents"""
        return [result.document.metadata for result in self.search_results]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'query': self.query,
            'retrieval_method': self.retrieval_method,
            'total_retrieved': self.total_retrieved,
            'retrieved_at': self.retrieved_at,
            'search_results': [result.to_dict() for result in self.search_results],
            'context_text': self.get_context_text(),
            'source_metadata': self.get_source_metadata()
        }


class RAGRetriever:
    """
    Retriever component of the RAG system
    Handles querying the vector database and returning relevant chunks
    """
    
    def __init__(self, 
                 vector_service_manager: VectorServiceManager,
                 default_k: int = 5,
                 default_similarity_threshold: float = 0.5):
        """
        Initialize RAG retriever
        
        Args:
            vector_service_manager: Vector service manager for database operations
            default_k: Default number of documents to retrieve
            default_similarity_threshold: Default similarity threshold
        """
        self.vector_service_manager = vector_service_manager
        self.default_k = default_k
        self.default_similarity_threshold = default_similarity_threshold
        
        logger.info("RAG Retriever initialized")
    
    def retrieve(self,
                query: str,
                k: Optional[int] = None,
                retrieval_method: str = "hybrid",
                metadata_filters: Optional[Dict[str, Any]] = None,
                similarity_threshold: Optional[float] = None,
                **kwargs) -> RetrievalResult:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            retrieval_method: Method to use ('semantic', 'text', 'hybrid')
            metadata_filters: Filters to apply
            similarity_threshold: Minimum similarity score
            **kwargs: Additional arguments for search
        
        Returns:
            RetrievalResult containing search results and metadata
        """
        try:
            k = k or self.default_k
            similarity_threshold = similarity_threshold or self.default_similarity_threshold
            
            # Perform search using vector service manager
            search_results = self.vector_service_manager.search(
                query=query,
                search_type=retrieval_method,
                n_results=k,
                metadata_filters=metadata_filters,
                **kwargs
            )
            
            # Create retrieval result
            retrieval_result = RetrievalResult(
                search_results=search_results,
                query=query,
                retrieval_method=retrieval_method,
                total_retrieved=len(search_results)
            )
            
            logger.info(f"Retrieved {len(search_results)} documents for query: '{query}'")
            return retrieval_result
            
        except Exception as e:
            logger.error(f"Error in retrieval: {e}")
            return RetrievalResult(
                search_results=[],
                query=query,
                retrieval_method=retrieval_method,
                total_retrieved=0
            )
    
    def get_retrieval_analytics(self) -> Dict[str, Any]:
        """Get analytics about retrieval performance"""
        try:
            system_status = self.vector_service_manager.get_system_status()
            
            analytics = {
                'total_documents_available': system_status.get('services', {}).get('document', {}).get('total_documents', 0),
                'vector_database_size': system_status.get('services', {}).get('chroma', {}).get('document_count', 0),
                'embedding_model': system_status.get('services', {}).get('embedding', {}),
                'default_k': self.default_k,
                'default_similarity_threshold': self.default_similarity_threshold,
                'supported_retrieval_methods': ['semantic', 'text', 'hybrid'],
                'capabilities': {
                    'category_filtering': True,
                    'source_filtering': True,
                    'date_range_filtering': True,
                    'metadata_filtering': True,
                    'similarity_threshold': True
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting retrieval analytics: {e}")
            return {'error': str(e)}


class RAGService:
    """
    Main RAG service that coordinates retrieval and LLM generation for end-to-end insights
    """
    
    def __init__(self, 
                 vector_service_manager: Optional[VectorServiceManager] = None,
                 llm_service: Optional[Any] = None,
                 retriever_config: Optional[Dict[str, Any]] = None):
        """
        Initialize RAG service
        
        Args:
            vector_service_manager: Vector service manager instance
            llm_service: LLM service instance
            retriever_config: Configuration for retriever
        """
        # Initialize vector service manager if not provided
        if vector_service_manager is None:
            # Load configuration from API config manager
            try:
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
                from config import get_vector_service_config
                vector_config = get_vector_service_config()
                vector_service_manager = create_vector_service_manager(config=vector_config)
            except Exception as e:
                logger.warning(f"Could not load vector service config: {e}")
                vector_service_manager = create_vector_service_manager()
        
        self.vector_service_manager = vector_service_manager
        
        # Initialize LLM service
        self.llm_service = llm_service
        if self.llm_service is None:
            try:
                # Import and initialize LLM service
                import sys
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
                from config import get_llm_config
                
                sys.path.append(os.path.dirname(__file__))
                from llm_service import create_llm_service
                
                llm_config = get_llm_config()
                self.llm_service = create_llm_service(llm_config)
                logger.info("LLM service initialized with configuration")
            except Exception as e:
                logger.warning(f"Could not initialize LLM service: {e}")
                self.llm_service = None
        
        # Initialize retriever
        retriever_config = retriever_config or {}
        self.retriever = RAGRetriever(
            vector_service_manager=vector_service_manager,
            default_k=retriever_config.get('default_k', 5),
            default_similarity_threshold=retriever_config.get('default_similarity_threshold', 0.5)
        )
        
        logger.info("RAG Service initialized")
    
    def retrieve_context(self,
                        query: str,
                        **kwargs) -> RetrievalResult:
        """
        Retrieve context for a query
        
        Args:
            query: Search query
            **kwargs: Additional arguments for retrieval
        
        Returns:
            RetrievalResult with retrieved documents
        """
        return self.retriever.retrieve(query=query, **kwargs)
    
    def generate_insights(self,
                         query: str,
                         retrieval_method: str = "hybrid",
                         insight_type: str = "general",
                         k: int = 5,
                         llm_provider: Optional[str] = None,
                         include_sources: bool = True,
                         **kwargs) -> Dict[str, Any]:
        """
        End-to-end pipeline: query → retrieval → LLM generation
        
        Args:
            query: User query
            retrieval_method: Method for retrieval ('semantic', 'text', 'hybrid')
            insight_type: Type of insight to generate
            k: Number of documents to retrieve
            llm_provider: LLM provider to use
            include_sources: Whether to include source documents in response
            **kwargs: Additional arguments
        
        Returns:
            Complete response with insights and metadata
        """
        try:
            pipeline_start_time = datetime.now()
            
            # Step 1: Retrieve relevant context
            logger.info(f"Starting retrieval for query: '{query}'")
            retrieval_result = self.retrieve_context(
                query=query,
                k=k,
                retrieval_method=retrieval_method,
                **kwargs
            )
            
            # Step 2: Prepare context for LLM
            context_text = retrieval_result.get_context_text()
            
            # Step 3: Generate insights using LLM
            llm_response = None
            if self.llm_service:
                logger.info(f"Generating insights using LLM")
                llm_response = self.llm_service.generate_insights(
                    query=query,
                    context=context_text,
                    provider=llm_provider,
                    insight_type=insight_type
                )
            else:
                logger.warning("LLM service not available, returning context only")
            
            # Step 4: Prepare complete response
            pipeline_end_time = datetime.now()
            total_time = (pipeline_end_time - pipeline_start_time).total_seconds()
            
            response = {
                'query': query,
                'insights': llm_response.content if llm_response else "LLM service not available",
                'retrieval': {
                    'method': retrieval_method,
                    'documents_found': retrieval_result.total_retrieved,
                    'context_length': len(context_text)
                },
                'generation': {
                    'provider': llm_response.provider if llm_response else None,
                    'model': llm_response.model if llm_response else None,
                    'tokens_used': llm_response.tokens_used if llm_response else None,
                    'response_time': llm_response.response_time if llm_response else None,
                    'insight_type': insight_type
                },
                'pipeline': {
                    'total_time': total_time,
                    'completed_at': pipeline_end_time.isoformat(),
                    'status': 'success' if llm_response else 'partial_success'
                }
            }
            
            # Include source documents if requested
            if include_sources:
                response['sources'] = [
                    {
                        'document_id': result.document.document_id,
                        'title': result.document.metadata.get('title', 'Untitled'),
                        'source': result.document.metadata.get('source', 'Unknown'),
                        'score': result.score,
                        'excerpt': result.document.text[:200] + "..." if len(result.document.text) > 200 else result.document.text
                    }
                    for result in retrieval_result.search_results
                ]
            
            logger.info(f"RAG pipeline completed in {total_time:.2f} seconds")
            return response
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            return {
                'query': query,
                'insights': f"Error generating insights: {str(e)}",
                'error': str(e),
                'pipeline': {
                    'status': 'error',
                    'completed_at': datetime.now().isoformat()
                }
            }
    
    def ask_question(self,
                    question: str,
                    context_filters: Optional[Dict[str, Any]] = None,
                    **kwargs) -> Dict[str, Any]:
        """
        Convenient method for asking questions with automatic insight type detection
        
        Args:
            question: User question
            context_filters: Optional filters for context retrieval
            **kwargs: Additional arguments
        
        Returns:
            Complete response with insights
        """
        # Simple insight type detection based on keywords
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['market', 'stock', 'trading', 'analysis', 'trends']):
            insight_type = 'market_analysis'
        elif any(word in question_lower for word in ['portfolio', 'investment', 'invest', 'allocat', 'risk']):
            insight_type = 'portfolio_advice'
        elif any(word in question_lower for word in ['news', 'latest', 'recent', 'update', 'event']):
            insight_type = 'news_summary'
        else:
            insight_type = 'general'
        
        return self.generate_insights(
            query=question,
            insight_type=insight_type,
            metadata_filters=context_filters,
            **kwargs
        )
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive RAG service status"""
        try:
            status = {
                'rag_service': {
                    'status': 'active',
                    'components': {
                        'retriever': 'active',
                        'llm_generator': 'active' if self.llm_service else 'not_available'
                    }
                },
                'vector_services': self.vector_service_manager.get_system_status(),
                'retrieval_analytics': self.retriever.get_retrieval_analytics(),
                'llm_service': self.llm_service.get_service_status() if self.llm_service else {'status': 'not_configured'},
                'pipeline_capabilities': {
                    'end_to_end_generation': self.llm_service is not None,
                    'supported_insight_types': ['general', 'market_analysis', 'portfolio_advice', 'news_summary'],
                    'supported_retrieval_methods': ['semantic', 'text', 'hybrid'],
                    'auto_question_categorization': True
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {'error': str(e)}


# Factory functions
def create_rag_service(vector_service_manager: Optional[VectorServiceManager] = None,
                      retriever_config: Optional[Dict[str, Any]] = None) -> RAGService:
    """
    Factory function to create a RAG service
    
    Args:
        vector_service_manager: Vector service manager instance
        retriever_config: Configuration for retriever
    
    Returns:
        Configured RAGService instance
    """
    return RAGService(
        vector_service_manager=vector_service_manager,
        retriever_config=retriever_config
    )


def get_default_rag_service() -> RAGService:
    """Get a default RAG service with recommended settings"""
    return create_rag_service()
