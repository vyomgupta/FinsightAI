"""
Data Ingestion Package for FinSightAI
"""

__version__ = "1.0.0"
__author__ = "FinSightAI Team"

# Import key functions for easy access
from .fetch_portfolio import mock_portfolio, ingest_portfolio_and_save
from .fetch_news import fetch_news_from_rss, fetch_news_by_category
from .clean_data import prepare_article_for_embeddings

__all__ = [
    'mock_portfolio',
    'ingest_portfolio_and_save', 
    'fetch_news_from_rss',
    'fetch_news_by_category',
    'prepare_article_for_embeddings'
]
