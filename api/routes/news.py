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
        return {
            "articles": [],
            "total": 0,
            "category": category,
            "message": "News endpoint placeholder - integrate with RSS scheduler data"
        }
    except Exception as e:
        logger.error(f"Error fetching latest news: {e}")
        raise HTTPException(status_code=500, detail="Error fetching news")

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
