"""
RSS Data Scheduler Service for FinSightAI
Automated RSS data fetching and vector database integration
"""
import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys
import os

# Add paths for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
data_ingest_path = project_root / "data-ingest"
vector_service_path = project_root / "vector-service"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(data_ingest_path))
sys.path.insert(0, str(vector_service_path))

# Import RSS and vector services
try:
    # Try different import patterns
    try:
        from rss_config import ALL_FEEDS, get_feeds_by_category, get_all_feed_urls
        from fetch_news import fetch_news_from_rss, fetch_news_by_category
        from clean_data import prepare_article_for_embeddings
    except ImportError:
        # Try with data-ingest prefix
        import sys
        sys.path.append(str(data_ingest_path))
        from rss_config import ALL_FEEDS, get_feeds_by_category, get_all_feed_urls
        from fetch_news import fetch_news_from_rss, fetch_news_by_category
        from clean_data import prepare_article_for_embeddings
    
    # Import vector service manager
    try:
        from vector_service_manager import create_vector_service_manager
    except ImportError:
        # Try with vector-service prefix
        sys.path.append(str(vector_service_path))
        from vector_service_manager import create_vector_service_manager
        
    vector_service_available = True
    logging.info("Successfully imported RSS and vector services")
    
except ImportError as e:
    logging.error(f"Import error in scheduler service: {e}")
    # Fallback imports
    ALL_FEEDS = []
    get_feeds_by_category = lambda x: []
    get_all_feed_urls = lambda: []
    fetch_news_from_rss = lambda x, **kwargs: []
    fetch_news_by_category = lambda x, **kwargs: []
    prepare_article_for_embeddings = lambda x: []
    create_vector_service_manager = lambda **kwargs: None
    vector_service_available = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RSSSchedulerService:
    """
    Service for scheduling and managing RSS data ingestion
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 vector_service_config: Optional[Dict[str, Any]] = None):
        """
        Initialize RSS Scheduler Service
        
        Args:
            config: Scheduler configuration
            vector_service_config: Vector service configuration
        """
        self.config = config or self._get_default_config()
        self.vector_service_manager = None
        self.running = False
        self.scheduler_thread = None
        self.last_fetch_time = None
        self.fetch_stats = {
            'total_fetches': 0,
            'successful_fetches': 0,
            'failed_fetches': 0,
            'total_articles': 0,
            'last_error': None
        }
        
        # Initialize vector service manager
        try:
            if vector_service_available and create_vector_service_manager != None:
                # Check if create_vector_service_manager is the real function or a lambda
                if hasattr(create_vector_service_manager, '__name__') and create_vector_service_manager.__name__ != '<lambda>':
                    # Use the correct parameter names for the vector service manager
                    base_dir = vector_service_config.get('base_dir', './vector_services') if vector_service_config else './vector_services'
                    self.vector_service_manager = create_vector_service_manager(
                        config=vector_service_config,
                        base_dir=base_dir
                    )
                    logger.info("Vector service manager initialized successfully")
                else:
                    logger.warning("Vector service manager not available (fallback lambda)")
                    self.vector_service_manager = None
            else:
                logger.warning("Vector service not available")
                self.vector_service_manager = None
        except Exception as e:
            logger.error(f"Failed to initialize vector service manager: {e}")
            self.vector_service_manager = None
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default scheduler configuration"""
        return {
            'fetch_interval_minutes': 30,  # Fetch every 30 minutes
            'max_articles_per_feed': 20,   # Limit articles per feed
            'categories_to_fetch': ['business', 'markets', 'analysis'],  # Categories to fetch
            'enable_all_feeds': False,     # Whether to fetch from all feeds
            'batch_size': 50,             # Batch size for processing
            'retry_attempts': 3,          # Retry attempts for failed feeds
            'timeout_seconds': 30,        # Request timeout
            'enable_on_startup': True,    # Run immediately on startup
            'cleanup_old_data': True,     # Clean up old data
            'max_data_age_days': 30      # Maximum age of data to keep
        }
    
    def start_scheduler(self) -> bool:
        """
        Start the RSS scheduler in a background thread
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.running:
            logger.warning("Scheduler is already running")
            return False
        
        if not self.vector_service_manager:
            logger.error("Cannot start scheduler: Vector service manager not available")
            return False
        
        try:
            self.running = True
            self.scheduler_thread = threading.Thread(
                target=self._scheduler_loop,
                daemon=True,
                name="RSS-Scheduler"
            )
            self.scheduler_thread.start()
            
            logger.info("RSS Scheduler started successfully")
            
            # Run initial fetch if configured
            if self.config.get('enable_on_startup', True):
                self._trigger_immediate_fetch()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start RSS scheduler: {e}")
            self.running = False
            return False
    
    def stop_scheduler(self) -> bool:
        """
        Stop the RSS scheduler
        
        Returns:
            True if stopped successfully, False otherwise
        """
        try:
            self.running = False
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=10)
            
            logger.info("RSS Scheduler stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping RSS scheduler: {e}")
            return False
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop running in background thread"""
        logger.info("RSS Scheduler loop started")
        
        interval_seconds = self.config.get('fetch_interval_minutes', 30) * 60
        
        while self.running:
            try:
                # Calculate next fetch time
                if self.last_fetch_time:
                    next_fetch_time = self.last_fetch_time + timedelta(seconds=interval_seconds)
                    
                    # Wait until it's time for the next fetch
                    while datetime.now() < next_fetch_time and self.running:
                        time.sleep(30)  # Check every 30 seconds
                
                if not self.running:
                    break
                
                # Perform RSS fetch
                self._perform_scheduled_fetch()
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                self.fetch_stats['failed_fetches'] += 1
                self.fetch_stats['last_error'] = str(e)
                
                # Wait before retrying
                time.sleep(60)
        
        logger.info("RSS Scheduler loop ended")
    
    def _trigger_immediate_fetch(self) -> None:
        """Trigger an immediate fetch in a separate thread"""
        def immediate_fetch():
            try:
                logger.info("Running immediate RSS fetch on startup")
                self._perform_scheduled_fetch()
            except Exception as e:
                logger.error(f"Error in immediate fetch: {e}")
        
        fetch_thread = threading.Thread(target=immediate_fetch, daemon=True)
        fetch_thread.start()
    
    def _perform_scheduled_fetch(self) -> None:
        """Perform the actual RSS data fetching and processing"""
        start_time = datetime.now()
        logger.info(f"Starting scheduled RSS fetch at {start_time}")
        
        try:
            self.fetch_stats['total_fetches'] += 1
            articles_processed = 0
            
            # Determine what to fetch
            if self.config.get('enable_all_feeds', False):
                # Fetch from all configured feeds
                feed_urls = get_all_feed_urls()
                articles = fetch_news_from_rss(
                    rss_urls=feed_urls,
                    max_entries_per_feed=self.config.get('max_articles_per_feed', 20),
                    timeout=self.config.get('timeout_seconds', 30),
                    retry_attempts=self.config.get('retry_attempts', 3)
                )
            else:
                # Fetch by categories
                articles = []
                categories = self.config.get('categories_to_fetch', ['business', 'markets'])
                
                for category in categories:
                    try:
                        category_articles = fetch_news_by_category(
                            category=category,
                            max_entries_per_feed=self.config.get('max_articles_per_feed', 20)
                        )
                        articles.extend(category_articles)
                        logger.info(f"Fetched {len(category_articles)} articles from {category} category")
                    except Exception as e:
                        logger.error(f"Error fetching {category} articles: {e}")
            
            if not articles:
                logger.warning("No articles fetched from RSS feeds")
                return
            
            logger.info(f"Fetched {len(articles)} total articles from RSS feeds")
            
            # Process articles for vector database
            processed_documents = []
            
            for article in articles:
                try:
                    # Prepare article for embeddings (chunking)
                    chunks = prepare_article_for_embeddings(article)
                    
                    for chunk in chunks:
                        # Format for vector service manager
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
                                'fetched_at': start_time.isoformat(),
                                'article_id': chunk.get('metadata', {}).get('article_id', ''),
                                'data_type': 'rss_news'
                            }
                        }
                        processed_documents.append(doc_data)
                        
                except Exception as e:
                    logger.error(f"Error processing article for embeddings: {e}")
                    continue
            
            if not processed_documents:
                logger.warning("No documents prepared for vector database")
                return
            
            # Add documents to vector database in batches
            batch_size = self.config.get('batch_size', 50)
            total_added = 0
            
            for i in range(0, len(processed_documents), batch_size):
                batch = processed_documents[i:i + batch_size]
                
                try:
                    added_ids = self.vector_service_manager.add_documents(
                        documents=batch,
                        generate_embeddings=True,
                        add_to_vector_db=True
                    )
                    total_added += len(added_ids)
                    logger.info(f"Added batch of {len(added_ids)} documents to vector database")
                    
                except Exception as e:
                    logger.error(f"Error adding document batch to vector database: {e}")
                    continue
            
            # Update statistics
            self.fetch_stats['successful_fetches'] += 1
            self.fetch_stats['total_articles'] += total_added
            self.last_fetch_time = start_time
            
            # Cleanup old data if configured
            if self.config.get('cleanup_old_data', True):
                self._cleanup_old_data()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"RSS fetch completed successfully in {duration:.2f} seconds")
            logger.info(f"Processed {len(articles)} articles into {total_added} documents")
            
        except Exception as e:
            logger.error(f"Error in scheduled RSS fetch: {e}")
            self.fetch_stats['failed_fetches'] += 1
            self.fetch_stats['last_error'] = str(e)
            raise
    
    def _cleanup_old_data(self) -> None:
        """Clean up old data from the vector database"""
        try:
            max_age_days = self.config.get('max_data_age_days', 30)
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            # Note: This would require implementing cleanup functionality
            # in the vector service manager
            logger.info(f"Cleanup would remove data older than {cutoff_date}")
            
        except Exception as e:
            logger.error(f"Error during data cleanup: {e}")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """
        Get current scheduler status and statistics
        
        Returns:
            Dictionary with scheduler status information
        """
        return {
            'running': self.running,
            'last_fetch_time': self.last_fetch_time.isoformat() if self.last_fetch_time else None,
            'next_fetch_time': (
                self.last_fetch_time + timedelta(
                    minutes=self.config.get('fetch_interval_minutes', 30)
                )
            ).isoformat() if self.last_fetch_time else None,
            'configuration': self.config,
            'statistics': self.fetch_stats,
            'vector_service_available': self.vector_service_manager is not None,
            'total_feeds_configured': len(ALL_FEEDS),
            'thread_alive': self.scheduler_thread.is_alive() if self.scheduler_thread else False
        }
    
    def trigger_manual_fetch(self) -> Dict[str, Any]:
        """
        Trigger a manual RSS fetch
        
        Returns:
            Status of the manual fetch trigger
        """
        if not self.running:
            return {
                'success': False,
                'message': 'Scheduler is not running'
            }
        
        try:
            # Trigger immediate fetch in background
            fetch_thread = threading.Thread(
                target=self._perform_scheduled_fetch,
                daemon=True,
                name="Manual-RSS-Fetch"
            )
            fetch_thread.start()
            
            return {
                'success': True,
                'message': 'Manual fetch triggered successfully',
                'triggered_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error triggering manual fetch: {e}")
            return {
                'success': False,
                'message': f'Error triggering manual fetch: {str(e)}'
            }
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Update scheduler configuration
        
        Args:
            new_config: New configuration dictionary
        
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            self.config.update(new_config)
            logger.info("Scheduler configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating scheduler configuration: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup scheduler resources"""
        try:
            self.stop_scheduler()
            
            if self.vector_service_manager:
                self.vector_service_manager.cleanup()
            
            logger.info("RSS Scheduler cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during scheduler cleanup: {e}")


# Global scheduler instance
_scheduler_instance: Optional[RSSSchedulerService] = None


def get_scheduler_service() -> Optional[RSSSchedulerService]:
    """Get the global scheduler service instance"""
    return _scheduler_instance


def initialize_scheduler_service(config: Optional[Dict[str, Any]] = None,
                               vector_config: Optional[Dict[str, Any]] = None) -> RSSSchedulerService:
    """
    Initialize the global scheduler service
    
    Args:
        config: Scheduler configuration
        vector_config: Vector service configuration
    
    Returns:
        Initialized scheduler service
    """
    global _scheduler_instance
    
    if _scheduler_instance is not None:
        logger.warning("Scheduler service already initialized")
        return _scheduler_instance
    
    try:
        _scheduler_instance = RSSSchedulerService(
            config=config,
            vector_service_config=vector_config
        )
        logger.info("Global scheduler service initialized")
        return _scheduler_instance
        
    except Exception as e:
        logger.error(f"Failed to initialize scheduler service: {e}")
        raise


def cleanup_scheduler_service() -> None:
    """Cleanup the global scheduler service"""
    global _scheduler_instance
    
    if _scheduler_instance:
        _scheduler_instance.cleanup()
        _scheduler_instance = None
        logger.info("Global scheduler service cleaned up")


if __name__ == "__main__":
    # Test the scheduler service
    try:
        # Initialize with test configuration
        test_config = {
            'fetch_interval_minutes': 1,  # 1 minute for testing
            'max_articles_per_feed': 5,
            'categories_to_fetch': ['business'],
            'enable_on_startup': True
        }
        
        scheduler = initialize_scheduler_service(config=test_config)
        
        # Start scheduler
        if scheduler.start_scheduler():
            print("Scheduler started successfully")
            
            # Let it run for a few minutes
            time.sleep(180)  # 3 minutes
            
            # Get status
            status = scheduler.get_scheduler_status()
            print(f"Scheduler status: {status}")
            
            # Stop scheduler
            scheduler.stop_scheduler()
            print("Scheduler stopped")
        else:
            print("Failed to start scheduler")
            
    except Exception as e:
        print(f"Error testing scheduler: {e}")
    finally:
        cleanup_scheduler_service()
