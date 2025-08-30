"""
Search Service for FinSightAI
Combines semantic search with metadata filtering for intelligent document retrieval
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import json

# Import our services
try:
    from .embedding_service import EmbeddingService
    from .chroma_service import ChromaService
    from .document_service import DocumentService, Document
except ImportError:
    from embedding_service import EmbeddingService
    from chroma_service import ChromaService
    from document_service import DocumentService, Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SearchResult:
    """
    Represents a search result with score and metadata
    """
    
    def __init__(self, 
                 document: Document,
                 score: float,
                 search_type: str = "semantic",
                 query: str = None):
        """
        Initialize search result
        
        Args:
            document: The document that matched
            score: Similarity score (0-1 for semantic, relevance for text)
            search_type: Type of search ('semantic', 'text', 'hybrid')
            query: Original search query
        """
        self.document = document
        self.score = score
        self.search_type = search_type
        self.query = query
        self.retrieved_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'document_id': self.document.document_id,
            'text': self.document.text,
            'metadata': self.document.metadata,
            'score': self.score,
            'search_type': self.search_type,
            'query': self.query,
            'retrieved_at': self.retrieved_at
        }
    
    def __repr__(self):
        return f"SearchResult(id={self.document.document_id}, score={self.score:.4f}, type={self.search_type})"


class SearchService:
    """
    Service for intelligent document search combining semantic and metadata approaches
    """
    
    def __init__(self,
                 embedding_service: EmbeddingService,
                 chroma_service: ChromaService,
                 document_service: DocumentService):
        """
        Initialize search service
        
        Args:
            embedding_service: Service for generating embeddings
            chroma_service: Service for vector database operations
            document_service: Service for document management
        """
        self.embedding_service = embedding_service
        self.chroma_service = chroma_service
        self.document_service = document_service
        
        logger.info("Search service initialized")
    
    def semantic_search(self, 
                       query: str,
                       n_results: int = 10,
                       metadata_filters: Optional[Dict[str, Any]] = None,
                       similarity_threshold: float = 0.5) -> List[SearchResult]:
        """
        Perform semantic search using vector similarity
        
        Args:
            query: Search query text
            n_results: Number of results to return
            metadata_filters: Metadata filters to apply
            similarity_threshold: Minimum similarity score (0-1)
        
        Returns:
            List of search results ordered by similarity score
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.encode(query)
            
            # Search in ChromaDB
            search_results = self.chroma_service.search_by_embedding(
                query_embedding=query_embedding,
                n_results=n_results * 2,  # Get more results for filtering
                where=metadata_filters
            )
            
            # Process results
            results = []
            for i in range(len(search_results['ids'][0])):
                doc_id = search_results['ids'][0][i]
                distance = search_results['distances'][0][i]
                
                # Convert distance to similarity score (assuming cosine distance)
                similarity_score = 1 - distance
                
                # Apply similarity threshold
                if similarity_score < similarity_threshold:
                    continue
                
                # Get document from document service
                doc = self.document_service.get_document(doc_id)
                if doc:
                    result = SearchResult(
                        document=doc,
                        score=similarity_score,
                        search_type="semantic",
                        query=query
                    )
                    results.append(result)
            
            # Sort by score (highest first) and limit results
            results.sort(key=lambda x: x.score, reverse=True)
            results = results[:n_results]
            
            logger.info(f"Semantic search returned {len(results)} results for query: '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def text_search(self, 
                   query: str,
                   n_results: int = 10,
                   metadata_filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """
        Perform text-based search using keyword matching
        
        Args:
            query: Search query text
            n_results: Number of results to return
            metadata_filters: Metadata filters to apply
        
        Returns:
            List of search results ordered by relevance
        """
        try:
            # Use document service for text search
            documents = self.document_service.search_documents(
                query=query,
                metadata_filters=metadata_filters,
                limit=n_results * 2
            )
            
            # Score documents based on query relevance
            scored_results = []
            query_terms = query.lower().split()
            
            for doc in documents:
                text_lower = doc.text.lower()
                
                # Calculate relevance score
                score = 0
                for term in query_terms:
                    if term in text_lower:
                        # Count occurrences and position
                        occurrences = text_lower.count(term)
                        first_pos = text_lower.find(term)
                        
                        # Score based on frequency and position
                        score += occurrences * 0.1
                        if first_pos < len(text_lower) * 0.3:  # Bonus for early appearance
                            score += 0.2
                
                # Normalize score
                if score > 0:
                    score = min(score, 1.0)  # Cap at 1.0
                    result = SearchResult(
                        document=doc,
                        score=score,
                        search_type="text",
                        query=query
                    )
                    scored_results.append(result)
            
            # Sort by score and limit results
            scored_results.sort(key=lambda x: x.score, reverse=True)
            scored_results = scored_results[:n_results]
            
            logger.info(f"Text search returned {len(scored_results)} results for query: '{query}'")
            return scored_results
            
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            return []
    
    def hybrid_search(self, 
                     query: str,
                     n_results: int = 10,
                     metadata_filters: Optional[Dict[str, Any]] = None,
                     semantic_weight: float = 0.7,
                     text_weight: float = 0.3) -> List[SearchResult]:
        """
        Perform hybrid search combining semantic and text approaches
        
        Args:
            query: Search query text
            n_results: Number of results to return
            metadata_filters: Metadata filters to apply
            semantic_weight: Weight for semantic search results (0-1)
            text_weight: Weight for text search results (0-1)
        
        Returns:
            List of search results with combined scoring
        """
        try:
            # Perform both searches
            semantic_results = self.semantic_search(
                query=query,
                n_results=n_results * 2,
                metadata_filters=metadata_filters
            )
            
            text_results = self.text_search(
                query=query,
                n_results=n_results * 2,
                metadata_filters=metadata_filters
            )
            
            # Combine results
            combined_results = {}
            
            # Process semantic results
            for result in semantic_results:
                doc_id = result.document.document_id
                combined_results[doc_id] = {
                    'document': result.document,
                    'semantic_score': result.score,
                    'text_score': 0.0,
                    'combined_score': result.score * semantic_weight
                }
            
            # Process text results
            for result in text_results:
                doc_id = result.document.document_id
                if doc_id in combined_results:
                    # Document exists in both results
                    combined_results[doc_id]['text_score'] = result.score
                    combined_results[doc_id]['combined_score'] += result.score * text_weight
                else:
                    # Document only in text results
                    combined_results[doc_id] = {
                        'document': result.document,
                        'semantic_score': 0.0,
                        'text_score': result.score,
                        'combined_score': result.score * text_weight
                    }
            
            # Convert to SearchResult objects
            final_results = []
            for doc_id, data in combined_results.items():
                result = SearchResult(
                    document=data['document'],
                    score=data['combined_score'],
                    search_type="hybrid",
                    query=query
                )
                final_results.append(result)
            
            # Sort by combined score and limit results
            final_results.sort(key=lambda x: x.score, reverse=True)
            final_results = final_results[:n_results]
            
            logger.info(f"Hybrid search returned {len(final_results)} results for query: '{query}'")
            return final_results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
    
    def search_by_category(self, 
                          category: str,
                          query: str = None,
                          n_results: int = 10,
                          search_type: str = "hybrid") -> List[SearchResult]:
        """
        Search within a specific category
        
        Args:
            category: Category to search in
            query: Optional search query
            n_results: Number of results to return
            search_type: Type of search to perform
        
        Returns:
            List of search results
        """
        metadata_filters = {'category': category}
        
        if search_type == "semantic":
            return self.semantic_search(query or category, n_results, metadata_filters)
        elif search_type == "text":
            return self.text_search(query or category, n_results, metadata_filters)
        else:
            return self.hybrid_search(query or category, n_results, metadata_filters)
    
    def search_by_source(self, 
                        source: str,
                        query: str = None,
                        n_results: int = 10,
                        search_type: str = "hybrid") -> List[SearchResult]:
        """
        Search within a specific source
        
        Args:
            source: Source to search in
            query: Optional search query
            n_results: Number of results to return
            search_type: Type of search to perform
        
        Returns:
            List of search results
        """
        metadata_filters = {'source': source}
        
        if search_type == "semantic":
            return self.semantic_search(query or source, n_results, metadata_filters)
        elif search_type == "text":
            return self.text_search(query or source, n_results, metadata_filters)
        else:
            return self.hybrid_search(query or source, n_results, metadata_filters)
    
    def advanced_search(self, 
                       query: str = None,
                       metadata_filters: Optional[Dict[str, Any]] = None,
                       date_range: Optional[Tuple[str, str]] = None,
                       n_results: int = 10,
                       search_type: str = "hybrid",
                       sort_by: str = "score") -> List[SearchResult]:
        """
        Advanced search with multiple filters and options
        
        Args:
            query: Search query text
            metadata_filters: Metadata filters to apply
            date_range: Tuple of (start_date, end_date) in ISO format
            n_results: Number of results to return
            search_type: Type of search to perform
            sort_by: Sort field ('score', 'date', 'title')
        
        Returns:
            List of search results
        """
        try:
            # Prepare filters
            filters = metadata_filters or {}
            
            # Add date range filter if provided
            if date_range:
                start_date, end_date = date_range
                filters['published'] = {
                    '$gte': start_date,
                    '$lte': end_date
                }
            
            # Perform search based on type
            if search_type == "semantic":
                results = self.semantic_search(query or "", n_results, filters)
            elif search_type == "text":
                results = self.text_search(query or "", n_results, filters)
            else:
                results = self.hybrid_search(query or "", n_results, filters)
            
            # Apply additional sorting if needed
            if sort_by == "date":
                results.sort(key=lambda x: x.document.metadata.get('published', ''), reverse=True)
            elif sort_by == "title":
                results.sort(key=lambda x: x.document.metadata.get('title', '').lower())
            # Default is already sorted by score
            
            logger.info(f"Advanced search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            return []
    
    def get_search_suggestions(self, 
                              partial_query: str,
                              max_suggestions: int = 5) -> List[str]:
        """
        Get search suggestions based on partial query
        
        Args:
            partial_query: Partial search query
            max_suggestions: Maximum number of suggestions
        
        Returns:
            List of suggested queries
        """
        try:
            suggestions = []
            
            # Get documents that contain the partial query
            documents = self.document_service.search_documents(
                query=partial_query,
                limit=50
            )
            
            # Extract potential suggestions from document titles and content
            for doc in documents:
                title = doc.metadata.get('title', '')
                if title and partial_query.lower() in title.lower():
                    # Extract relevant part of title
                    words = title.split()
                    for i, word in enumerate(words):
                        if partial_query.lower() in word.lower():
                            # Get surrounding context
                            start = max(0, i - 2)
                            end = min(len(words), i + 3)
                            suggestion = ' '.join(words[start:end])
                            if suggestion not in suggestions:
                                suggestions.append(suggestion)
                                if len(suggestions) >= max_suggestions:
                                    break
                    if len(suggestions) >= max_suggestions:
                        break
            
            # Add category-based suggestions
            if len(suggestions) < max_suggestions:
                summary = self.document_service.get_metadata_summary()
                categories = list(summary.get('categories', {}).keys())
                
                for category in categories:
                    if partial_query.lower() in category.lower():
                        suggestion = f"category:{category}"
                        if suggestion not in suggestions:
                            suggestions.append(suggestion)
                            if len(suggestions) >= max_suggestions:
                                break
            
            return suggestions[:max_suggestions]
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            return []
    
    def get_search_analytics(self, 
                           time_period: str = "7d") -> Dict[str, Any]:
        """
        Get search analytics and statistics
        
        Args:
            time_period: Time period for analytics ('1d', '7d', '30d', 'all')
        
        Returns:
            Search analytics data
        """
        try:
            # Get document summary
            summary = self.document_service.get_metadata_summary()
            
            # Get collection info
            collection_info = self.chroma_service.get_collection_info()
            
            analytics = {
                'total_documents': summary.get('total_documents', 0),
                'vector_database_size': collection_info.get('document_count', 0),
                'categories': summary.get('categories', {}),
                'sources': summary.get('sources', {}),
                'embedding_model': self.embedding_service.get_model_info(),
                'search_capabilities': {
                    'semantic_search': True,
                    'text_search': True,
                    'hybrid_search': True,
                    'metadata_filtering': True,
                    'category_search': True,
                    'source_search': True
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting search analytics: {e}")
            return {}


# Factory function for easy service creation
def create_search_service(embedding_service: EmbeddingService,
                         chroma_service: ChromaService,
                         document_service: DocumentService) -> SearchService:
    """
    Factory function to create a search service
    
    Args:
        embedding_service: Service for generating embeddings
        chroma_service: Service for vector database operations
        document_service: Service for document management
    
    Returns:
        Configured SearchService instance
    """
    return SearchService(
        embedding_service=embedding_service,
        chroma_service=chroma_service,
        document_service=document_service
    )


if __name__ == "__main__":
    # Test the search service
    try:
        # Create services (this would normally be done with proper configuration)
        from embedding_service import get_default_embedding_service
        from chroma_service import create_chroma_service
        from document_service import create_document_service
        
        embedding_service = get_default_embedding_service()
        chroma_service = create_chroma_service()
        document_service = create_document_service()
        
        # Create search service
        search_service = create_search_service(
            embedding_service=embedding_service,
            chroma_service=chroma_service,
            document_service=document_service
        )
        
        # Test search
        results = search_service.hybrid_search("finance", n_results=5)
        print(f"Search returned {len(results)} results")
        
        # Get analytics
        analytics = search_service.get_search_analytics()
        print(f"Search analytics: {analytics}")
        
    except Exception as e:
        print(f"Error testing search service: {e}")
