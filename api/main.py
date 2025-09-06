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

# Load environment variables from .env file
load_dotenv()

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'routes'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FinSightAI API",
    description="Financial Intelligence Platform with RAG and LLM capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
        "endpoints": {
            "chat": "/query/insights",
            "news": "/news/latest",
            "portfolio": "/portfolio",
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
