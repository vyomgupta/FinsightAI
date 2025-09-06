# FinSightAI API Reference

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required (development mode).

---

## 📋 Table of Contents
1. [General Information](#general-information)
2. [Query & Insights Endpoints](#query--insights-endpoints)
3. [News Endpoints](#news-endpoints)
4. [Portfolio Endpoints](#portfolio-endpoints)
5. [Scheduler Endpoints](#scheduler-endpoints)
6. [System Endpoints](#system-endpoints)
7. [Error Handling](#error-handling)
8. [Data Models](#data-models)

---

## 🔧 General Information

### Content Types
- **Request**: `application/json`
- **Response**: `application/json`

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable

---

## 💬 Query & Insights Endpoints

### POST /query/insights
Submit a query to the AI system for intelligent insights.

**Request Body:**
```json
{
  "query": "What are the latest market trends?",
  "context": "optional context information",
  "max_results": 10,
  "search_type": "hybrid"
}
```

**Parameters:**
- `query` (string, required): The question or query to process
- `context` (string, optional): Additional context for the query
- `max_results` (integer, optional): Maximum number of results to return (default: 10)
- `search_type` (string, optional): Type of search - "semantic", "text", or "hybrid" (default: "hybrid")

**Response:**
```json
{
  "response": "AI-generated response based on vector search results",
  "sources": [
    {
      "title": "Article Title",
      "url": "https://example.com/article",
      "relevance_score": 0.95,
      "source": "Reuters",
      "published": "2024-01-01T00:00:00Z",
      "category": "business"
    }
  ],
  "metadata": {
    "search_time": "0.123s",
    "results_count": 5,
    "query_processed": "What are the latest market trends?",
    "search_type": "hybrid"
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/query/insights" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current state of the cryptocurrency market?",
    "max_results": 5
  }'
```

---

## 📰 News Endpoints

### GET /news/latest
Get the latest news articles.

**Query Parameters:**
- `category` (string, optional): Filter by category (business, markets, analysis, crypto, regional, commodities)
- `limit` (integer, optional): Maximum number of articles to return (default: 20)
- `source` (string, optional): Filter by news source
- `hours` (integer, optional): Get articles from last N hours (default: 24)

**Response:**
```json
{
  "articles": [
    {
      "id": "article_123",
      "title": "Market Update: Stocks Rise on Positive Earnings",
      "summary": "Stock markets showed strong performance...",
      "content": "Full article content...",
      "url": "https://example.com/article",
      "source": "Reuters",
      "category": "markets",
      "published": "2024-01-01T10:00:00Z",
      "fetched_at": "2024-01-01T10:05:00Z"
    }
  ],
  "metadata": {
    "total_count": 25,
    "returned_count": 20,
    "filters_applied": {
      "category": "markets",
      "limit": 20
    },
    "fetch_time": "2024-01-01T10:05:00Z"
  }
}
```

### GET /news/search
Search news articles by query.

**Query Parameters:**
- `query` (string, required): Search query
- `category` (string, optional): Filter by category
- `limit` (integer, optional): Maximum results (default: 10)
- `search_type` (string, optional): "semantic", "text", or "hybrid" (default: "hybrid")

**Response:**
```json
{
  "articles": [
    {
      "id": "article_456",
      "title": "Bitcoin Reaches New All-Time High",
      "summary": "Cryptocurrency market shows strong momentum...",
      "content": "Full article content...",
      "url": "https://example.com/bitcoin-news",
      "source": "CoinDesk",
      "category": "crypto",
      "published": "2024-01-01T09:00:00Z",
      "relevance_score": 0.92
    }
  ],
  "metadata": {
    "query": "bitcoin price",
    "total_results": 15,
    "returned_count": 10,
    "search_time": "0.045s"
  }
}
```

### GET /news/categories
Get available news categories and their article counts.

**Response:**
```json
{
  "categories": [
    {
      "name": "business",
      "display_name": "Business",
      "article_count": 45,
      "description": "Business and corporate news"
    },
    {
      "name": "markets",
      "display_name": "Markets",
      "article_count": 38,
      "description": "Financial markets and trading"
    }
  ],
  "total_articles": 150
}
```

---

## 💼 Portfolio Endpoints

### GET /portfolio
Get all portfolio items.

**Response:**
```json
{
  "portfolios": [
    {
      "id": "portfolio_1",
      "name": "Tech Stocks",
      "description": "Technology sector investments",
      "items": [
        {
          "symbol": "AAPL",
          "name": "Apple Inc.",
          "quantity": 100,
          "purchase_price": 150.00,
          "current_price": 175.50,
          "value": 17550.00,
          "gain_loss": 2550.00,
          "gain_loss_percent": 17.0
        }
      ],
      "total_value": 17550.00,
      "total_gain_loss": 2550.00,
      "total_gain_loss_percent": 17.0,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "metadata": {
    "total_portfolios": 1,
    "total_value": 17550.00
  }
}
```

### POST /portfolio
Create a new portfolio.

**Request Body:**
```json
{
  "name": "My Investment Portfolio",
  "description": "Personal investment portfolio",
  "items": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "quantity": 100,
      "purchase_price": 150.00
    }
  ]
}
```

**Response:**
```json
{
  "portfolio": {
    "id": "portfolio_2",
    "name": "My Investment Portfolio",
    "description": "Personal investment portfolio",
    "items": [
      {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "quantity": 100,
        "purchase_price": 150.00,
        "current_price": 175.50,
        "value": 17550.00,
        "gain_loss": 2550.00,
        "gain_loss_percent": 17.0
      }
    ],
    "total_value": 17550.00,
    "total_gain_loss": 2550.00,
    "total_gain_loss_percent": 17.0,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "message": "Portfolio created successfully"
}
```

### PUT /portfolio/{portfolio_id}
Update an existing portfolio.

**Request Body:**
```json
{
  "name": "Updated Portfolio Name",
  "description": "Updated description",
  "items": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "quantity": 150,
      "purchase_price": 160.00
    }
  ]
}
```

### DELETE /portfolio/{portfolio_id}
Delete a portfolio.

**Response:**
```json
{
  "message": "Portfolio deleted successfully",
  "deleted_id": "portfolio_1"
}
```

---

## ⏰ Scheduler Endpoints

### GET /scheduler/status
Get the current status of the RSS scheduler.

**Response:**
```json
{
  "status": "running",
  "is_running": true,
  "last_fetch": "2024-01-01T10:00:00Z",
  "next_fetch": "2024-01-01T10:30:00Z",
  "statistics": {
    "total_feeds": 24,
    "active_feeds": 22,
    "failed_feeds": 2,
    "articles_fetched": 450,
    "articles_processed": 445,
    "processing_time": "2.5s"
  },
  "configuration": {
    "fetch_interval_minutes": 30,
    "max_articles_per_feed": 20,
    "categories_to_fetch": ["business", "markets", "analysis"],
    "enable_all_feeds": false
  }
}
```

### POST /scheduler/start
Start the RSS scheduler.

**Response:**
```json
{
  "success": true,
  "message": "Scheduler started successfully",
  "status": "running"
}
```

### POST /scheduler/stop
Stop the RSS scheduler.

**Response:**
```json
{
  "success": true,
  "message": "Scheduler stopped successfully",
  "status": "stopped"
}
```

### POST /scheduler/trigger
Trigger a manual RSS data fetch.

**Response:**
```json
{
  "success": true,
  "message": "Manual fetch triggered successfully",
  "fetch_id": "fetch_123",
  "estimated_completion": "2024-01-01T10:05:00Z"
}
```

### PUT /scheduler/config
Update scheduler configuration.

**Request Body:**
```json
{
  "fetch_interval_minutes": 60,
  "max_articles_per_feed": 30,
  "categories_to_fetch": ["business", "markets", "analysis", "crypto"],
  "enable_all_feeds": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration updated successfully",
  "new_config": {
    "fetch_interval_minutes": 60,
    "max_articles_per_feed": 30,
    "categories_to_fetch": ["business", "markets", "analysis", "crypto"],
    "enable_all_feeds": true
  }
}
```

---

## 🔧 System Endpoints

### GET /
Get basic API information.

**Response:**
```json
{
  "message": "FinSightAI API is running",
  "version": "1.0.0",
  "status": "online",
  "rss_scheduler": {
    "available": true,
    "status_endpoint": "/scheduler/status"
  },
  "endpoints": {
    "chat": "/query/insights",
    "news": "/news/latest",
    "portfolio": "/portfolio",
    "scheduler": "/scheduler/status",
    "docs": "/docs"
  }
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "FinSightAI API",
  "timestamp": "2024-01-01T12:00:00Z",
  "components": {
    "database": "healthy",
    "vector_service": "healthy",
    "scheduler": "healthy"
  }
}
```

### GET /docs
Interactive API documentation (Swagger UI).

### GET /redoc
Alternative API documentation (ReDoc).

---

## ❌ Error Handling

### Error Response Format
```json
{
  "detail": "Error message",
  "error": "Detailed error information",
  "status_code": 400,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common Error Codes

#### 400 Bad Request
```json
{
  "detail": "Invalid request parameters",
  "error": "Missing required field: query",
  "status_code": 400
}
```

#### 404 Not Found
```json
{
  "detail": "Resource not found",
  "error": "Portfolio with ID 'portfolio_999' not found",
  "status_code": 404
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error": "Vector service initialization failed",
  "status_code": 500
}
```

#### 503 Service Unavailable
```json
{
  "detail": "Service temporarily unavailable",
  "error": "Scheduler service not available",
  "status_code": 503
}
```

---

## 📊 Data Models

### Article Model
```json
{
  "id": "string",
  "title": "string",
  "summary": "string",
  "content": "string",
  "url": "string",
  "source": "string",
  "category": "string",
  "published": "datetime",
  "fetched_at": "datetime",
  "relevance_score": "float (optional)"
}
```

### Portfolio Item Model
```json
{
  "symbol": "string",
  "name": "string",
  "quantity": "number",
  "purchase_price": "number",
  "current_price": "number",
  "value": "number",
  "gain_loss": "number",
  "gain_loss_percent": "number"
}
```

### Portfolio Model
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "items": "PortfolioItem[]",
  "total_value": "number",
  "total_gain_loss": "number",
  "total_gain_loss_percent": "number",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Search Result Model
```json
{
  "title": "string",
  "url": "string",
  "relevance_score": "number",
  "source": "string",
  "published": "datetime",
  "category": "string"
}
```

---

## 🔍 Examples

### Complete Workflow Example

1. **Start the scheduler:**
```bash
curl -X POST "http://localhost:8000/scheduler/start"
```

2. **Check scheduler status:**
```bash
curl -X GET "http://localhost:8000/scheduler/status"
```

3. **Get latest news:**
```bash
curl -X GET "http://localhost:8000/news/latest?category=markets&limit=5"
```

4. **Ask a question:**
```bash
curl -X POST "http://localhost:8000/query/insights" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the top performing stocks today?"}'
```

5. **Create a portfolio:**
```bash
curl -X POST "http://localhost:8000/portfolio" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Portfolio",
    "items": [
      {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "quantity": 100,
        "purchase_price": 150.00
      }
    ]
  }'
```

---

## 📝 Notes

- All timestamps are in ISO 8601 format (UTC)
- All monetary values are in USD
- The API supports CORS for frontend integration
- Rate limiting may be implemented in production
- Authentication will be added in future versions

---

**FinSightAI API** - Financial Intelligence Platform API Reference 🚀
