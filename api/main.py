"""
FinSightAI FastAPI Application
Main entry point for the financial intelligence platform
"""
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load environment variables from .env file
load_dotenv()

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'routes'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import scheduler service
try:
    from services.scheduler_service import initialize_scheduler_service, cleanup_scheduler_service, get_scheduler_service
    scheduler_available = True
except ImportError as e:
    logger.warning(f"Scheduler service not available: {e}")
    scheduler_available = False

# Lifespan event handler for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events"""
    logger.info("Starting FinSightAI application...")
    
    # Startup: Initialize RSS scheduler (but don't auto-start)
    if scheduler_available:
        try:
            # Load scheduler configuration from environment
            scheduler_config = {
                'fetch_interval_minutes': int(os.getenv('RSS_FETCH_INTERVAL_MINUTES', '30')),
                'max_articles_per_feed': int(os.getenv('RSS_MAX_ARTICLES_PER_FEED', '20')),
                'categories_to_fetch': os.getenv('RSS_CATEGORIES', 'business,markets,analysis').split(','),
                'enable_all_feeds': os.getenv('RSS_ENABLE_ALL_FEEDS', 'false').lower() == 'true',
                'batch_size': int(os.getenv('RSS_BATCH_SIZE', '50')),
                'enable_on_startup': os.getenv('RSS_ENABLE_ON_STARTUP', 'false').lower() == 'true',  # Changed default to 'false'
                'cleanup_old_data': os.getenv('RSS_CLEANUP_OLD_DATA', 'true').lower() == 'true',
                'max_data_age_days': int(os.getenv('RSS_MAX_DATA_AGE_DAYS', '30'))
            }
            
            # Vector service configuration
            vector_config = {
                'embedding': {
                    'model_name': os.getenv('EMBEDDING_MODEL_NAME', 'jina-embeddings-v3'),
                    'model_type': os.getenv('EMBEDDING_MODEL_TYPE', 'jina'),
                    'jina_api_key': os.getenv('JINA_API_KEY'),
                    'cache_dir': os.getenv('EMBEDDING_CACHE_DIR', './vector_services/embeddings')
                },
                'chroma': {
                    'persist_directory': os.getenv('CHROMA_PERSIST_DIR', './vector_services/chroma_db'),
                    'collection_name': os.getenv('CHROMA_COLLECTION_NAME', 'finsight_documents')
                },
                'document': {
                    'storage_dir': os.getenv('DOCUMENT_STORAGE_DIR', './vector_services/documents')
                }
            }
            
            # Initialize scheduler service but DON'T auto-start it
            scheduler = initialize_scheduler_service(
                config=scheduler_config,
                vector_config=vector_config
            )
            
            # Only start if explicitly enabled via environment variable
            if scheduler_config.get('enable_on_startup', False):
                if scheduler.start_scheduler():
                    logger.info("RSS Scheduler started successfully (auto-start enabled)")
                else:
                    logger.error("Failed to start RSS scheduler")
            else:
                logger.info("RSS Scheduler initialized but not started (auto-start disabled). Use /scheduler/start endpoint to start manually.")
                
        except Exception as e:
            logger.error(f"Failed to initialize RSS scheduler: {e}")
    else:
        logger.warning("RSS Scheduler not available - running without automated data ingestion")
    
    yield  # Application runs here
    
    # Shutdown: Clean up scheduler
    if scheduler_available:
        try:
            cleanup_scheduler_service()
            logger.info("RSS Scheduler cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up RSS scheduler: {e}")
    
    logger.info("FinSightAI application shutdown complete")

# Create FastAPI app with lifespan events
app = FastAPI(
    title="FinSightAI API",
    description="Financial Intelligence Platform with RAG and LLM capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
try:
    from query import router as query_router
    app.include_router(query_router)
    logger.info("Query router loaded successfully")
except ImportError as e:
    logger.warning(f"Could not load query router: {e}")

try:
    from news import router as news_router
    app.include_router(news_router)
    logger.info("News router loaded successfully")
except ImportError as e:
    logger.warning(f"Could not load news router: {e}")

try:
    from portfolio import router as portfolio_router
    app.include_router(portfolio_router)
    logger.info("Portfolio router loaded successfully")
except ImportError as e:
    logger.warning(f"Could not load portfolio router: {e}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "FinSightAI API is running",
        "version": "1.0.0",
        "status": "online",
        "rss_scheduler": {
            "available": scheduler_available,
            "status_endpoint": "/scheduler/status" if scheduler_available else None
        },
        "endpoints": {
            "chat": "/query/insights",
            "news": "/news/latest",
            "portfolio": "/portfolio",
            "scheduler": "/scheduler/status",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "FinSightAI API",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# RSS Scheduler Management Endpoints
@app.get("/scheduler/status")
async def get_scheduler_status():
    """Get RSS scheduler status and statistics"""
    if not scheduler_available:
        raise HTTPException(status_code=503, detail="Scheduler service not available")
    
    scheduler = get_scheduler_service()
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")
    
    return scheduler.get_scheduler_status()

@app.post("/scheduler/trigger")
async def trigger_manual_fetch():
    """Trigger a manual RSS data fetch"""
    if not scheduler_available:
        raise HTTPException(status_code=503, detail="Scheduler service not available")
    
    scheduler = get_scheduler_service()
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")
    
    result = scheduler.trigger_manual_fetch()
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result

@app.post("/scheduler/start")
async def start_scheduler():
    """Start the RSS scheduler"""
    if not scheduler_available:
        raise HTTPException(status_code=503, detail="Scheduler service not available")
    
    scheduler = get_scheduler_service()
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")
    
    if scheduler.start_scheduler():
        return {"success": True, "message": "Scheduler started successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to start scheduler")

@app.post("/scheduler/stop")
async def stop_scheduler():
    """Stop the RSS scheduler"""
    if not scheduler_available:
        raise HTTPException(status_code=503, detail="Scheduler service not available")
    
    scheduler = get_scheduler_service()
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")
    
    if scheduler.stop_scheduler():
        return {"success": True, "message": "Scheduler stopped successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to stop scheduler")

@app.put("/scheduler/config")
async def update_scheduler_config(config: dict):
    """Update scheduler configuration"""
    if not scheduler_available:
        raise HTTPException(status_code=503, detail="Scheduler service not available")
    
    scheduler = get_scheduler_service()
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")
    
    if scheduler.update_config(config):
        return {"success": True, "message": "Configuration updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to update configuration")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
