#!/usr/bin/env python3
"""
FinSightAI RSS Scheduler Startup Script
Standalone script to run the RSS scheduler independently
"""
import os
import sys
import json
import signal
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "api" / "services"))
sys.path.append(str(project_root / "data-ingest"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / "logs" / "scheduler.log", mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
(project_root / "logs").mkdir(exist_ok=True)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load scheduler configuration from file or environment
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        Configuration dictionary
    """
    config = {}
    
    # Load from JSON file if provided
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
                logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading config file {config_path}: {e}")
    
    # Load default config file if no specific path provided
    elif not config_path:
        default_config_path = project_root / "scheduler_config.json"
        if default_config_path.exists():
            try:
                with open(default_config_path, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
                    logger.info(f"Loaded default configuration from {default_config_path}")
            except Exception as e:
                logger.error(f"Error loading default config: {e}")
    
    # Override with environment variables
    env_config = {
        'scheduler': {
            'fetch_interval_minutes': int(os.getenv('RSS_FETCH_INTERVAL_MINUTES', 
                                                  config.get('scheduler', {}).get('fetch_interval_minutes', 30))),
            'max_articles_per_feed': int(os.getenv('RSS_MAX_ARTICLES_PER_FEED', 
                                                 config.get('scheduler', {}).get('max_articles_per_feed', 20))),
            'categories_to_fetch': os.getenv('RSS_CATEGORIES', 
                                           ','.join(config.get('scheduler', {}).get('categories_to_fetch', 
                                                                                   ['business', 'markets', 'analysis']))).split(','),
            'enable_all_feeds': os.getenv('RSS_ENABLE_ALL_FEEDS', 
                                        str(config.get('scheduler', {}).get('enable_all_feeds', False))).lower() == 'true',
            'batch_size': int(os.getenv('RSS_BATCH_SIZE', 
                                      config.get('scheduler', {}).get('batch_size', 50))),
            'enable_on_startup': os.getenv('RSS_ENABLE_ON_STARTUP', 
                                         str(config.get('scheduler', {}).get('enable_on_startup', True))).lower() == 'true',
            'cleanup_old_data': os.getenv('RSS_CLEANUP_OLD_DATA', 
                                        str(config.get('scheduler', {}).get('cleanup_old_data', True))).lower() == 'true',
            'max_data_age_days': int(os.getenv('RSS_MAX_DATA_AGE_DAYS', 
                                             config.get('scheduler', {}).get('max_data_age_days', 30)))
        },
        'vector_service': {
            'embedding': {
                'model_name': os.getenv('EMBEDDING_MODEL_NAME', 
                                      config.get('vector_service', {}).get('embedding', {}).get('model_name', 'jina-embeddings-v3')),
                'model_type': os.getenv('EMBEDDING_MODEL_TYPE', 
                                      config.get('vector_service', {}).get('embedding', {}).get('model_type', 'jina')),
                'jina_api_key': os.getenv('JINA_API_KEY', 
                                        config.get('vector_service', {}).get('embedding', {}).get('jina_api_key')),
                'cache_dir': os.getenv('EMBEDDING_CACHE_DIR', 
                                     config.get('vector_service', {}).get('embedding', {}).get('cache_dir', './vector_services/embeddings'))
            },
            'chroma': {
                'persist_directory': os.getenv('CHROMA_PERSIST_DIR', 
                                             config.get('vector_service', {}).get('chroma', {}).get('persist_directory', './vector_services/chroma_db')),
                'collection_name': os.getenv('CHROMA_COLLECTION_NAME', 
                                           config.get('vector_service', {}).get('chroma', {}).get('collection_name', 'finsight_documents'))
            },
            'document': {
                'storage_dir': os.getenv('DOCUMENT_STORAGE_DIR', 
                                       config.get('vector_service', {}).get('document', {}).get('storage_dir', './vector_services/documents'))
            }
        }
    }
    
    # Merge configurations
    final_config = {
        'scheduler': env_config['scheduler'],
        'vector_service': env_config['vector_service']
    }
    
    return final_config


def main():
    """Main function to start the RSS scheduler"""
    logger.info("Starting FinSightAI RSS Scheduler...")
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='FinSightAI RSS Scheduler')
    parser.add_argument('--config', '-c', type=str, help='Path to configuration file')
    parser.add_argument('--interval', '-i', type=int, help='Fetch interval in minutes')
    parser.add_argument('--categories', type=str, help='Comma-separated list of categories to fetch')
    parser.add_argument('--all-feeds', action='store_true', help='Fetch from all configured feeds')
    parser.add_argument('--no-startup-fetch', action='store_true', help='Disable immediate fetch on startup')
    parser.add_argument('--dry-run', action='store_true', help='Run without actually storing data')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override with command line arguments
    if args.interval:
        config['scheduler']['fetch_interval_minutes'] = args.interval
    
    if args.categories:
        config['scheduler']['categories_to_fetch'] = [cat.strip() for cat in args.categories.split(',')]
    
    if args.all_feeds:
        config['scheduler']['enable_all_feeds'] = True
    
    if args.no_startup_fetch:
        config['scheduler']['enable_on_startup'] = False
    
    logger.info(f"Configuration: {json.dumps(config, indent=2)}")
    
    # Initialize scheduler
    scheduler = None
    try:
        from scheduler_service import initialize_scheduler_service, cleanup_scheduler_service
        
        scheduler = initialize_scheduler_service(
            config=config['scheduler'],
            vector_config=config['vector_service']
        )
        
        logger.info("Scheduler service initialized successfully")
        
        # Start the scheduler
        if scheduler.start_scheduler():
            logger.info("RSS Scheduler started successfully")
            
            # Set up signal handlers for graceful shutdown
            def signal_handler(signum, frame):
                logger.info(f"Received signal {signum}, shutting down gracefully...")
                if scheduler:
                    scheduler.stop_scheduler()
                cleanup_scheduler_service()
                logger.info("Scheduler shutdown complete")
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Print status information
            status = scheduler.get_scheduler_status()
            logger.info(f"Scheduler Status: {json.dumps(status, indent=2, default=str)}")
            
            # Keep the scheduler running
            logger.info("Scheduler is running. Press Ctrl+C to stop.")
            
            try:
                import time
                while True:
                    time.sleep(60)  # Check every minute
                    
                    # Periodically log status
                    if hasattr(scheduler, 'fetch_stats'):
                        stats = scheduler.fetch_stats
                        logger.info(f"Scheduler stats - Total fetches: {stats.get('total_fetches', 0)}, "
                                  f"Successful: {stats.get('successful_fetches', 0)}, "
                                  f"Failed: {stats.get('failed_fetches', 0)}, "
                                  f"Total articles: {stats.get('total_articles', 0)}")
                        
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received, shutting down...")
                scheduler.stop_scheduler()
                
        else:
            logger.error("Failed to start RSS scheduler")
            sys.exit(1)
            
    except ImportError as e:
        logger.error(f"Failed to import scheduler service: {e}")
        logger.error("Make sure the scheduler service dependencies are installed")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        sys.exit(1)
        
    finally:
        # Cleanup
        if scheduler:
            scheduler.cleanup()
        cleanup_scheduler_service()
        logger.info("Cleanup completed")


if __name__ == "__main__":
    main()
