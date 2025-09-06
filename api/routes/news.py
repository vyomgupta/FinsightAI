"""
News endpoints for FinSightAI API
Provides access to financial news data and RSS feed management
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/news", tags=["news"])

@router.get("/latest")
async def get_latest_news(
    category: Optional[str] = Query(None, description="News category filter"),
    limit: int = Query(50, description="Number of articles to return")
):
    """Get latest news articles"""
    try:
        # Placeholder implementation - you can integrate with your vector service here
        # Return empty array directly to match frontend expectations
        return []
    except Exception as e:
        logger.error(f"Error fetching latest news: {e}")
        raise HTTPException(status_code=500, detail="Error fetching news")

@router.get("/category/{category}")
async def get_news_by_category(
    category: str,
    limit: int = Query(10, description="Number of articles to return")
):
    """Get news articles by category"""
    try:
        # Placeholder implementation - you can integrate with your vector service here
        # Return empty array directly to match frontend expectations
        return []
    except Exception as e:
        logger.error(f"Error fetching news by category: {e}")
        raise HTTPException(status_code=500, detail="Error fetching news by category")

@router.get("/search")
async def search_news(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Number of articles to return")
):
    """Search news articles"""
    try:
        # Placeholder implementation - you can integrate with your vector service here
        # Return empty array directly to match frontend expectations
        return []
    except Exception as e:
        logger.error(f"Error searching news: {e}")
        raise HTTPException(status_code=500, detail="Error searching news")

@router.get("/categories")
async def get_news_categories():
    """Get available news categories"""
    try:
        categories = ["business", "markets", "analysis", "crypto", "regional"]
        return {
            "categories": categories,
            "total": len(categories)
        }
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail="Error fetching categories")

@router.get("/sources")
async def get_news_sources():
    """Get available RSS news sources"""
    try:
        # You can integrate with RSS config here
        return {
            "sources": [
                {"name": "Reuters Business", "category": "business"},
                {"name": "Bloomberg Markets", "category": "markets"},
                {"name": "CNBC Business", "category": "business"},
                # Add more sources as needed
            ],
            "total_feeds": 22,
            "message": "RSS sources from scheduler configuration"
        }
    except Exception as e:
        logger.error(f"Error fetching sources: {e}")
        raise HTTPException(status_code=500, detail="Error fetching sources")
