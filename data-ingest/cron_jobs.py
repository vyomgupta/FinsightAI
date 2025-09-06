# data_ingest/cron_jobs.py
"""
Enhanced cron jobs with vector service integration
Legacy scheduler functions - use scheduler_service.py for new implementations
"""
import time
import schedule
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import local modules
from .fetch_portfolio import mock_portfolio
from .fetch_news import ingest_rss_and_save, fetch_news_from_rss, fetch_news_by_category
from .clean_data import prepare_article_for_embeddings
from .utils import LOG

# Add path for vector service imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root / "vector-service"))

# Import vector service manager
try:
    from vector_service.vector_service_manager import create_vector_service_manager
    vector_service_available = True
except ImportError as e:
    LOG.warning(f"Vector service not available: {e}")
    vector_service_available = False


def run_periodic_ingestion_with_vector_db(rss_feeds: List[str], 
                                        interval_minutes: int = 30, 
                                        use_vector_db: bool = True,
                                        demo: bool = True):
    """
    Enhanced periodic ingestion with vector database support
    
    Args:
        rss_feeds: List of RSS feed URLs
        interval_minutes: Interval between fetches in minutes
        use_vector_db: Whether to use vector database for storage
        demo: Whether to run in demo mode
    """
    LOG.info("Starting enhanced periodic ingestion scheduler")
    
    # Initialize vector service manager if available
    vector_manager = None
    if use_vector_db and vector_service_available:
        try:
            vector_manager = create_vector_service_manager()
            LOG.info("Vector service manager initialized for cron jobs")
        except Exception as e:
            LOG.error(f"Failed to initialize vector service manager: {e}")
            vector_manager = None

    def enhanced_job():
        """Enhanced job function with vector database integration"""
        LOG.info("Running enhanced scheduled ingestion job")
        try:
            # Portfolio ingestion (existing functionality)
            try:
                from .fetch_portfolio import fetch_portfolio_from_api, ingest_portfolio_and_save
                from api.utils.config import get_portfolio_api_config

                portfolio_config = get_portfolio_api_config()
                portfolio_api_url = portfolio_config.get("url")
                portfolio_api_key = portfolio_config.get("api_key")

                if portfolio_api_url:
                    LOG.info("Fetching portfolio from actual API")
                    p = fetch_portfolio_from_api(api_url=portfolio_api_url, api_key=portfolio_api_key)
                    ingest_portfolio_and_save(p, filename=f"portfolio_{int(time.time())}.json")
                else:
                    LOG.warning("Portfolio API URL not configured. Skipping actual portfolio ingestion.")
            except Exception as e:
                LOG.error(f"Portfolio ingestion failed: {e}")

            # RSS News ingestion with vector database
            if vector_manager:
                LOG.info("Fetching RSS news with vector database integration")
                
                # Fetch articles
                articles = fetch_news_from_rss(
                    rss_urls=rss_feeds,
                    max_entries_per_feed=20,
                    timeout=30,
                    retry_attempts=3
                )
                
                if articles:
                    LOG.info(f"Fetched {len(articles)} articles from RSS feeds")
                    
                    # Process articles for vector database
                    processed_documents = []
                    
                    for article in articles:
                        try:
                            chunks = prepare_article_for_embeddings(article)
                            
                            for chunk in chunks:
                                doc_data = {
                                    'text': chunk['text'],
                                    'id': chunk.get('id'),
                                    'metadata': {
                                        'title': article.get('title', ''),
                                        'source': article.get('source', ''),
                                        'feed_title': article.get('feed_title', ''),
                                        'published': article.get('published', ''),
                                        'link': article.get('link', ''),
                                        'category': chunk.get('metadata', {}).get('category', 'news'),
                                        'chunk_index': chunk.get('metadata', {}).get('chunk_index', 0),
                                        'total_chunks': chunk.get('metadata', {}).get('total_chunks', 1),
                                        'fetched_at': time.time(),
                                        'article_id': chunk.get('metadata', {}).get('article_id', ''),
                                        'data_type': 'rss_news',
                                        'ingestion_method': 'cron_job'
                                    }
                                }
                                processed_documents.append(doc_data)
                                
                        except Exception as e:
                            LOG.error(f"Error processing article for embeddings: {e}")
                            continue
                    
                    # Add to vector database in batches
                    if processed_documents:
                        batch_size = 50
                        total_added = 0
                        
                        for i in range(0, len(processed_documents), batch_size):
                            batch = processed_documents[i:i + batch_size]
                            
                            try:
                                added_ids = vector_manager.add_documents(
                                    documents=batch,
                                    generate_embeddings=True,
                                    add_to_vector_db=True
                                )
                                total_added += len(added_ids)
                                LOG.info(f"Added batch of {len(added_ids)} documents to vector database")
                                
                            except Exception as e:
                                LOG.error(f"Error adding document batch to vector database: {e}")
                                continue
                        
                        LOG.info(f"Successfully added {total_added} documents to vector database")
                    else:
                        LOG.warning("No documents processed for vector database")
                else:
                    LOG.warning("No articles fetched from RSS feeds")
            else:
                # Fallback to file-based storage
                LOG.info("Using file-based storage (vector database not available)")
                ingest_rss_and_save(rss_feeds, filename=f"rss_{int(time.time())}.json")
                
        except Exception as e:
            LOG.exception(f"Enhanced scheduled ingestion failed: {e}")

    # Schedule the enhanced job
    schedule.every(interval_minutes).minutes.do(enhanced_job)
    enhanced_job()  # run once immediately
    
    LOG.info(f"Scheduler will run every {interval_minutes} minutes")
    
    while True:
        schedule.run_pending()
        time.sleep(1)


def run_periodic_ingestion(rss_feeds, interval_minutes: int = 30, demo: bool = True):
    """
    Legacy periodic ingestion function (maintained for backward compatibility)
    """
    LOG.info("Starting legacy periodic ingestion scheduler")

    def job():
        LOG.info("Running scheduled ingestion job")
        try:
            from .fetch_portfolio import fetch_portfolio_from_api, ingest_portfolio_and_save
            from api.utils.config import get_portfolio_api_config # Assuming this config exists or will be created

            portfolio_config = get_portfolio_api_config()
            portfolio_api_url = portfolio_config.get("url")
            portfolio_api_key = portfolio_config.get("api_key")

            if portfolio_api_url:
                LOG.info("Fetching portfolio from actual API")
                p = fetch_portfolio_from_api(api_url=portfolio_api_url, api_key=portfolio_api_key)
                ingest_portfolio_and_save(p, filename=f"portfolio_{int(time.time())}.json")
            else:
                LOG.warning("Portfolio API URL not configured. Skipping actual portfolio ingestion.")

            ingest_rss_and_save(rss_feeds, filename=f"rss_{int(time.time())}.json")
        except Exception as e:
            LOG.exception(f"Scheduled ingestion failed: {e}")

    schedule.every(interval_minutes).minutes.do(job)
    job()  # run once immediately
    while True:
        schedule.run_pending()
        time.sleep(1)


def run_category_based_ingestion(categories: List[str] = None, 
                                interval_minutes: int = 30,
                                use_vector_db: bool = True):
    """
    Category-based RSS ingestion with vector database support
    
    Args:
        categories: List of categories to fetch (business, markets, analysis, crypto, regional)
        interval_minutes: Interval between fetches in minutes
        use_vector_db: Whether to use vector database for storage
    """
    if categories is None:
        categories = ['business', 'markets', 'analysis']
    
    LOG.info(f"Starting category-based ingestion for categories: {categories}")
    
    # Initialize vector service manager if available
    vector_manager = None
    if use_vector_db and vector_service_available:
        try:
            vector_manager = create_vector_service_manager()
            LOG.info("Vector service manager initialized for category-based ingestion")
        except Exception as e:
            LOG.error(f"Failed to initialize vector service manager: {e}")
            vector_manager = None

    def category_job():
        """Job function for category-based ingestion"""
        LOG.info(f"Running category-based ingestion for: {categories}")
        
        try:
            all_articles = []
            
            # Fetch articles by category
            for category in categories:
                try:
                    category_articles = fetch_news_by_category(category, max_entries_per_feed=20)
                    all_articles.extend(category_articles)
                    LOG.info(f"Fetched {len(category_articles)} articles from {category} category")
                except Exception as e:
                    LOG.error(f"Error fetching {category} articles: {e}")
            
            if not all_articles:
                LOG.warning("No articles fetched from any category")
                return
            
            LOG.info(f"Total articles fetched: {len(all_articles)}")
            
            # Process with vector database if available
            if vector_manager:
                processed_documents = []
                
                for article in all_articles:
                    try:
                        chunks = prepare_article_for_embeddings(article)
                        
                        for chunk in chunks:
                            doc_data = {
                                'text': chunk['text'],
                                'id': chunk.get('id'),
                                'metadata': {
                                    'title': article.get('title', ''),
                                    'source': article.get('source', ''),
                                    'feed_title': article.get('feed_title', ''),
                                    'published': article.get('published', ''),
                                    'link': article.get('link', ''),
                                    'category': chunk.get('metadata', {}).get('category', 'news'),
                                    'chunk_index': chunk.get('metadata', {}).get('chunk_index', 0),
                                    'total_chunks': chunk.get('metadata', {}).get('total_chunks', 1),
                                    'fetched_at': time.time(),
                                    'article_id': chunk.get('metadata', {}).get('article_id', ''),
                                    'data_type': 'rss_news',
                                    'ingestion_method': 'category_based_cron'
                                }
                            }
                            processed_documents.append(doc_data)
                            
                    except Exception as e:
                        LOG.error(f"Error processing article for embeddings: {e}")
                        continue
                
                # Add to vector database
                if processed_documents:
                    try:
                        added_ids = vector_manager.add_documents(
                            documents=processed_documents,
                            generate_embeddings=True,
                            add_to_vector_db=True
                        )
                        LOG.info(f"Added {len(added_ids)} documents to vector database")
                    except Exception as e:
                        LOG.error(f"Error adding documents to vector database: {e}")
            else:
                # Fallback to file storage
                from .utils import save_json, DATA_DIR
                timestamp = int(time.time())
                filename = f"category_articles_{timestamp}.json"
                save_json(all_articles, DATA_DIR / filename)
                LOG.info(f"Saved {len(all_articles)} articles to {filename}")
                
        except Exception as e:
            LOG.exception(f"Category-based ingestion failed: {e}")

    # Schedule the category job
    schedule.every(interval_minutes).minutes.do(category_job)
    category_job()  # run once immediately
    
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    example_rss = [
        'https://economictimes.indiatimes.com/feeds/rssfeedstopstories.cms',
        'https://www.moneycontrol.com/rss/MCtopnews.xml',
        'https://www.reuters.com/finance/markets/rss'
    ]
    run_periodic_ingestion(example_rss, interval_minutes=30, demo=False)
