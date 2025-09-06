# FinSightAI RSS Scheduler Guide

## 🚀 Automated RSS Data Ingestion

The FinSightAI RSS Scheduler automatically fetches financial news from 22+ RSS feeds and integrates them into your vector database for AI-powered analysis.

## ✨ Key Features

### 📰 Comprehensive RSS Sources
- **22 RSS feeds** across 5 categories:
  - **Major Financial News** (6 feeds): Reuters, Bloomberg, CNBC, MarketWatch, Financial Times, Yahoo Finance
  - **Specialized Analysis** (9 feeds): Seeking Alpha, Investing.com, The Street, Motley Fool, ETF.com, Kitco, OilPrice, Zero Hedge, Wolf Street
  - **Cryptocurrency** (3 feeds): CoinDesk, Cointelegraph, Decrypt
  - **Regional Markets** (2 feeds): Asia Times Finance, European Business Review

### 🤖 AI-Powered Integration
- **Vector Database Storage**: Automatic embedding generation and ChromaDB integration
- **Smart Chunking**: Articles are intelligently split for optimal embedding performance
- **Semantic Search Ready**: All content is immediately searchable via your RAG system

### ⚙️ Flexible Configuration
- **Configurable Intervals**: Set custom fetch intervals (default: 30 minutes)
- **Category Selection**: Choose specific news categories to fetch
- **Rate Limiting**: Configurable articles per feed and batch processing
- **Error Handling**: Robust retry logic and graceful failure handling

## 🏗️ Architecture

### Integration Points
1. **FastAPI Application**: Automatically starts with your main app
2. **Vector Service Manager**: Seamless integration with ChromaDB and embeddings
3. **REST API Endpoints**: Monitor and control the scheduler via HTTP
4. **Background Processing**: Non-blocking operation with thread-based scheduling

### Data Flow
```
RSS Feeds → Fetch Articles → Clean & Chunk → Generate Embeddings → Store in ChromaDB → Ready for RAG Queries
```

## 🚀 Quick Start

### Method 1: Automatic with FastAPI (Recommended)
The scheduler automatically starts when you run your FinSightAI application:

```bash
# Start the full application (includes scheduler)
cd api
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The scheduler will:
- ✅ Start automatically on application startup
- ✅ Fetch RSS data every 30 minutes (configurable)
- ✅ Store data in your vector database
- ✅ Be available via REST API endpoints

### Method 2: Standalone Scheduler
Run the scheduler independently:

```bash
# Run with default configuration
python scripts/start_scheduler.py

# Run with custom interval (15 minutes)
python scripts/start_scheduler.py --interval 15

# Run with specific categories
python scripts/start_scheduler.py --categories "business,markets,crypto"

# Run with all feeds enabled
python scripts/start_scheduler.py --all-feeds

# Run with custom config file
python scripts/start_scheduler.py --config my_config.json
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in your project root:

```bash
# RSS Scheduler Configuration
RSS_FETCH_INTERVAL_MINUTES=30
RSS_MAX_ARTICLES_PER_FEED=20
RSS_CATEGORIES=business,markets,analysis
RSS_ENABLE_ALL_FEEDS=false
RSS_BATCH_SIZE=50
RSS_ENABLE_ON_STARTUP=true
RSS_CLEANUP_OLD_DATA=true
RSS_MAX_DATA_AGE_DAYS=30

# Vector Service Configuration
EMBEDDING_MODEL_NAME=jina-embeddings-v3
EMBEDDING_MODEL_TYPE=jina
JINA_API_KEY=your_jina_api_key_here
CHROMA_PERSIST_DIR=./vector_services/chroma_db
CHROMA_COLLECTION_NAME=finsight_documents
DOCUMENT_STORAGE_DIR=./vector_services/documents
```

### JSON Configuration File
Use `scheduler_config.json` for detailed configuration:

```json
{
  "scheduler": {
    "fetch_interval_minutes": 30,
    "max_articles_per_feed": 20,
    "categories_to_fetch": ["business", "markets", "analysis"],
    "enable_all_feeds": false,
    "batch_size": 50,
    "enable_on_startup": true,
    "cleanup_old_data": true,
    "max_data_age_days": 30
  },
  "vector_service": {
    "embedding": {
      "model_name": "jina-embeddings-v3",
      "model_type": "jina",
      "cache_dir": "./vector_services/embeddings"
    },
    "chroma": {
      "persist_directory": "./vector_services/chroma_db",
      "collection_name": "finsight_documents"
    }
  }
}
```

## 🎛️ REST API Control

Monitor and control the scheduler via HTTP endpoints:

### Get Scheduler Status
```bash
GET /scheduler/status
```
Returns detailed status including:
- Running state
- Last fetch time
- Next scheduled fetch
- Statistics (total fetches, articles processed, errors)
- Configuration details

### Trigger Manual Fetch
```bash
POST /scheduler/trigger
```
Immediately triggers an RSS data fetch (non-blocking).

### Start/Stop Scheduler
```bash
POST /scheduler/start    # Start the scheduler
POST /scheduler/stop     # Stop the scheduler
```

### Update Configuration
```bash
PUT /scheduler/config
Content-Type: application/json

{
  "fetch_interval_minutes": 15,
  "categories_to_fetch": ["business", "markets"]
}
```

## 📊 Monitoring & Debugging

### Check Application Status
```bash
curl http://localhost:8000/scheduler/status
```

### View Logs
```bash
# Application logs
tail -f logs/finsight.log

# Scheduler-specific logs
tail -f logs/scheduler.log
```

### Example Status Response
```json
{
  "running": true,
  "last_fetch_time": "2024-01-15T10:30:00",
  "next_fetch_time": "2024-01-15T11:00:00",
  "configuration": {
    "fetch_interval_minutes": 30,
    "categories_to_fetch": ["business", "markets", "analysis"]
  },
  "statistics": {
    "total_fetches": 48,
    "successful_fetches": 47,
    "failed_fetches": 1,
    "total_articles": 1250
  },
  "vector_service_available": true,
  "total_feeds_configured": 22
}
```

## 🎯 Usage Scenarios

### Development Mode
```bash
# Quick testing with frequent updates
RSS_FETCH_INTERVAL_MINUTES=5 RSS_MAX_ARTICLES_PER_FEED=5 python -m uvicorn api.main:app --reload
```

### Production Mode
```bash
# Stable operation with comprehensive fetching
RSS_FETCH_INTERVAL_MINUTES=30 RSS_CATEGORIES=business,markets,analysis,crypto python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Category-Specific Fetching
```bash
# Focus on cryptocurrency news
RSS_CATEGORIES=crypto RSS_ENABLE_ALL_FEEDS=false python scripts/start_scheduler.py
```

### High-Volume Mode
```bash
# Fetch from all sources
RSS_ENABLE_ALL_FEEDS=true RSS_MAX_ARTICLES_PER_FEED=50 python scripts/start_scheduler.py
```

## 🔧 Advanced Configuration

### Custom Feed Selection
Modify `data-ingest/rss_config.py` to add custom RSS feeds:

```python
CUSTOM_FEEDS = [
    RSSFeed(
        name="Your Custom Feed",
        url="https://your-site.com/rss",
        category="custom",
        description="Your custom financial news source"
    )
]

# Add to ALL_FEEDS
ALL_FEEDS = MAJOR_NEWS_FEEDS + SPECIALIZED_FEEDS + CRYPTO_FEEDS + REGIONAL_FEEDS + CUSTOM_FEEDS
```

### Error Handling
The scheduler includes comprehensive error handling:
- **Retry Logic**: Failed feeds are retried with exponential backoff
- **Graceful Degradation**: Individual feed failures don't stop the entire process
- **Detailed Logging**: All errors are logged with context
- **Statistics Tracking**: Monitor success/failure rates

### Performance Tuning
Optimize for your infrastructure:

```json
{
  "scheduler": {
    "batch_size": 100,           // Larger batches for high-memory systems
    "max_articles_per_feed": 50, // More articles per fetch
    "timeout_seconds": 60,       // Longer timeout for slow networks
    "retry_attempts": 5          // More retries for unreliable networks
  }
}
```

## 🚨 Troubleshooting

### Common Issues

#### Scheduler Not Starting
```bash
# Check if vector services are available
python -c "from vector_service.vector_service_manager import create_vector_service_manager; print('Vector service OK')"

# Check RSS configuration
python -c "from data_ingest.rss_config import ALL_FEEDS; print(f'{len(ALL_FEEDS)} feeds configured')"
```

#### No Articles Being Fetched
1. Check internet connectivity
2. Verify RSS feed URLs are accessible
3. Check logs for specific error messages
4. Try manual fetch: `POST /scheduler/trigger`

#### Vector Database Issues
1. Verify Jina API key is set: `echo $JINA_API_KEY`
2. Check ChromaDB directory permissions
3. Ensure sufficient disk space

### Debug Mode
Run with detailed logging:

```bash
LOG_LEVEL=DEBUG python scripts/start_scheduler.py
```

## 📈 Performance Metrics

### Expected Performance
- **Startup Time**: 10-30 seconds (depending on vector service initialization)
- **Fetch Cycle**: 2-5 minutes for all feeds (depending on network and processing speed)
- **Memory Usage**: 200-500MB (depending on batch size and vector service)
- **Storage**: ~1-5MB per day of RSS data (compressed embeddings)

### Optimization Tips
1. **Adjust Batch Size**: Larger batches = faster processing, more memory usage
2. **Limit Categories**: Fewer categories = faster fetching, less comprehensive data
3. **Tune Intervals**: Shorter intervals = fresher data, more resource usage
4. **Monitor Disk Space**: Vector databases can grow large over time

## 🔒 Security Considerations

- **API Keys**: Store sensitive keys in environment variables, not config files
- **Network Access**: Scheduler requires outbound internet access to RSS feeds
- **File Permissions**: Ensure vector database directories have proper permissions
- **Rate Limiting**: Built-in rate limiting prevents overwhelming RSS sources

## 🎯 Next Steps

1. **Monitor Performance**: Use the status endpoints to monitor scheduler health
2. **Customize Sources**: Add your preferred financial news RSS feeds
3. **Tune Configuration**: Adjust intervals and categories based on your needs
4. **Integrate with RAG**: Query the automatically populated vector database
5. **Scale Up**: Consider multiple scheduler instances for high-volume scenarios

The RSS Scheduler is now fully integrated into your FinSightAI application, providing continuous, AI-ready financial news data for enhanced insights and analysis! 🚀
