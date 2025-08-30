"""
Chat/RAG API Endpoints for FinSightAI
Provides intelligent query processing with retrieval-augmented generation
"""
import os
import sys
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/query", tags=["RAG Query"])

# Initialize RAG service (will be done lazily)
_rag_service = None


def get_rag_service():
    """Get or initialize RAG service"""
    global _rag_service
    if _rag_service is None:
        try:
            from rag_service import get_default_rag_service
            _rag_service = get_default_rag_service()
            logger.info("RAG service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise HTTPException(status_code=500, detail=f"RAG service initialization failed: {str(e)}")
    
    return _rag_service


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for RAG queries"""
    query: str = Field(..., description="The user's question or query", min_length=1, max_length=1000)
    retrieval_method: str = Field("hybrid", description="Method for document retrieval", pattern="^(semantic|text|hybrid)$")
    insight_type: str = Field("general", description="Type of insight to generate", pattern="^(general|market_analysis|portfolio_advice|news_summary)$")
    k: int = Field(5, description="Number of documents to retrieve", ge=1, le=20)
    llm_provider: Optional[str] = Field(None, description="LLM provider to use (openai, gemini)")
    include_sources: bool = Field(True, description="Include source documents in response")
    metadata_filters: Optional[Dict[str, Any]] = Field(None, description="Filters for document retrieval")


class SimpleQueryRequest(BaseModel):
    """Simplified request model for basic queries"""
    question: str = Field(..., description="The user's question", min_length=1, max_length=1000)
    category: Optional[str] = Field(None, description="Optional category filter")
    source: Optional[str] = Field(None, description="Optional source filter")


class RetrievalRequest(BaseModel):
    """Request model for retrieval-only queries"""
    query: str = Field(..., description="Search query", min_length=1, max_length=1000)
    method: str = Field("hybrid", description="Retrieval method", pattern="^(semantic|text|hybrid)$")
    k: int = Field(10, description="Number of documents to retrieve", ge=1, le=50)
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")


class InsightResponse(BaseModel):
    """Response model for RAG insights"""
    query: str
    insights: str
    retrieval: Dict[str, Any]
    generation: Dict[str, Any]
    pipeline: Dict[str, Any]
    sources: Optional[List[Dict[str, Any]]] = None


class ServiceStatusResponse(BaseModel):
    """Response model for service status"""
    rag_service: Dict[str, Any]
    vector_services: Dict[str, Any]
    llm_service: Dict[str, Any]
    pipeline_capabilities: Dict[str, Any]


# API Endpoints
@router.post("/insights", response_model=InsightResponse)
async def generate_insights(request: QueryRequest) -> Dict[str, Any]:
    """
    Generate AI insights based on query with full control over parameters
    
    This endpoint provides the complete RAG pipeline: retrieval + generation
    """
    try:
        rag_service = get_rag_service()
        
        response = rag_service.generate_insights(
            query=request.query,
            retrieval_method=request.retrieval_method,
            insight_type=request.insight_type,
            k=request.k,
            llm_provider=request.llm_provider,
            include_sources=request.include_sources,
            metadata_filters=request.metadata_filters
        )
        
        logger.info(f"Generated insights for query: '{request.query[:50]}...'")
        return response
        
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")


@router.post("/ask")
async def ask_question(request: SimpleQueryRequest) -> Dict[str, Any]:
    """
    Ask a question with automatic categorization and smart defaults
    
    This is the simplified endpoint for general use with automatic insight type detection
    """
    try:
        rag_service = get_rag_service()
        
        # Prepare context filters
        context_filters = {}
        if request.category:
            context_filters['category'] = request.category
        if request.source:
            context_filters['source'] = request.source
        
        response = rag_service.ask_question(
            question=request.question,
            context_filters=context_filters if context_filters else None
        )
        
        logger.info(f"Answered question: '{request.question[:50]}...'")
        return response
        
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")


@router.post("/retrieve")
async def retrieve_documents(request: RetrievalRequest) -> Dict[str, Any]:
    """
    Retrieve relevant documents without LLM generation
    
    This endpoint provides only the retrieval part of the RAG pipeline
    """
    try:
        rag_service = get_rag_service()
        
        retrieval_result = rag_service.retrieve_context(
            query=request.query,
            k=request.k,
            retrieval_method=request.method,
            metadata_filters=request.filters
        )
        
        # Convert to API response format
        response = {
            'query': request.query,
            'method': request.method,
            'total_retrieved': retrieval_result.total_retrieved,
            'retrieved_at': retrieval_result.retrieved_at,
            'context_text': retrieval_result.get_context_text(),
            'documents': [
                {
                    'document_id': result.document.document_id,
                    'text': result.document.text,
                    'metadata': result.document.metadata,
                    'score': result.score
                }
                for result in retrieval_result.search_results
            ]
        }
        
        logger.info(f"Retrieved {retrieval_result.total_retrieved} documents for query: '{request.query[:50]}...'")
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")


@router.get("/status", response_model=ServiceStatusResponse)
async def get_service_status() -> Dict[str, Any]:
    """
    Get comprehensive status of the RAG service and all components
    """
    try:
        rag_service = get_rag_service()
        status = rag_service.get_service_status()
        
        logger.info("Service status retrieved")
        return status
        
    except Exception as e:
        logger.error(f"Error getting service status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get service status: {str(e)}")


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Simple health check endpoint
    """
    try:
        # Quick health check
        rag_service = get_rag_service()
        
        # Test basic functionality
        test_result = rag_service.retrieve_context(
            query="health check",
            k=1,
            retrieval_method="hybrid"
        )
        
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'components': {
                'rag_service': 'active',
                'vector_database': 'active' if test_result.total_retrieved >= 0 else 'inactive',
                'llm_service': 'active' if rag_service.llm_service else 'not_configured'
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }


@router.get("/capabilities")
async def get_capabilities() -> Dict[str, Any]:
    """
    Get information about RAG service capabilities
    """
    try:
        rag_service = get_rag_service()
        status = rag_service.get_service_status()
        
        capabilities = {
            'retrieval_methods': ['semantic', 'text', 'hybrid'],
            'insight_types': ['general', 'market_analysis', 'portfolio_advice', 'news_summary'],
            'llm_providers': status.get('llm_service', {}).get('available_providers', []),
            'features': {
                'auto_question_categorization': True,
                'source_filtering': True,
                'metadata_filtering': True,
                'similarity_threshold': True,
                'performance_metrics': True,
                'source_attribution': True
            },
            'limits': {
                'max_query_length': 1000,
                'max_retrieval_docs': 50,
                'max_insight_docs': 20
            }
        }
        
        return capabilities
        
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")


# Query parameter endpoints for simple GET requests
@router.get("/simple")
async def simple_query(
    q: str = Query(..., description="Question to ask", min_length=1, max_length=500),
    type: str = Query("auto", description="Insight type or 'auto' for automatic detection"),
    k: int = Query(5, description="Number of documents to retrieve", ge=1, le=10)
) -> Dict[str, Any]:
    """
    Simple GET endpoint for basic queries
    """
    try:
        rag_service = get_rag_service()
        
        if type == "auto":
            response = rag_service.ask_question(question=q, k=k)
        else:
            response = rag_service.generate_insights(
                query=q,
                insight_type=type,
                k=k
            )
        
        logger.info(f"Simple query processed: '{q[:50]}...'")
        return response
        
    except Exception as e:
        logger.error(f"Error processing simple query: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")


@router.get("/search")
async def search_documents(
    q: str = Query(..., description="Search query", min_length=1),
    method: str = Query("hybrid", description="Search method"),
    limit: int = Query(10, description="Number of results", ge=1, le=50),
    category: Optional[str] = Query(None, description="Category filter"),
    source: Optional[str] = Query(None, description="Source filter")
) -> Dict[str, Any]:
    """
    Simple GET endpoint for document search
    """
    try:
        # Prepare filters
        filters = {}
        if category:
            filters['category'] = category
        if source:
            filters['source'] = source
        
        request = RetrievalRequest(
            query=q,
            method=method,
            k=limit,
            filters=filters if filters else None
        )
        
        return await retrieve_documents(request)
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search documents: {str(e)}")
