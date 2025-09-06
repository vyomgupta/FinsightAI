# FinSightAI Architecture Diagram

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                FinSightAI Platform                              │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Vector DB     │    │   Data Sources  │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (ChromaDB)    │◄──►│   (RSS Feeds)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Components │    │   Services      │    │   Vector Store  │    │   Data Pipeline │
│   - ChatBot     │    │   - LLM Service │    │   - Embeddings  │    │   - RSS Parser  │
│   - NewsView    │    │   - RAG Service │    │   - Documents   │    │   - Data Clean  │
│   - Portfolio   │    │   - Scheduler   │    │   - Metadata    │    │   - Text Chunk  │
│   - Dashboard   │    │   - Vector Mgr  │    │   - Search      │    │   - NewsAPI     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔄 Data Flow Architecture

```
┌─────────────────┐
│   RSS Feeds     │
│   (24 sources)  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Ingestion│    │   Text Cleaning │    │   Text Chunking │
│   - fetch_news  │───►│   - clean_data  │───►│   - prepare_    │
│   - RSS Parser  │    │   - normalize   │    │     embeddings  │
└─────────────────┘    └─────────────────┘    └─────────┬───────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vector Store  │◄───│   Embeddings    │◄───│   Jina API      │
│   - ChromaDB    │    │   - 1024 dims   │    │   - v3 Model    │
│   - HNSW Index  │    │   - Semantic    │    │   - Fast API    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Search Engine │    │   RAG Service   │    │   LLM Service   │
│   - Hybrid      │───►│   - Context     │───►│   - Gemini      │
│   - Semantic    │    │   - Retrieval   │    │   - Response    │
│   - Text Match  │    │   - Generation  │    │   - Generation  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐
│   API Response  │
│   - Formatted   │
│   - Sources     │
│   - Metadata    │
└─────────────────┘
```

## 🏛️ Component Architecture

### Frontend Layer (React)
```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend                           │
├─────────────────────────────────────────────────────────────┤
│  App.tsx (Main Router)                                      │
│  ├── ChatBot.tsx (AI Chat Interface)                       │
│  ├── NewsInsights.tsx (News Display)                       │
│  ├── PortfolioView.tsx (Portfolio Management)              │
│  └── Dashboard.tsx (System Overview)                       │
├─────────────────────────────────────────────────────────────┤
│  Services Layer                                             │
│  └── apiClient.ts (HTTP Client)                            │
├─────────────────────────────────────────────────────────────┤
│  UI Framework: Material-UI (MUI)                           │
│  Charts: Recharts, MUI X Charts                            │
│  State: React Hooks                                         │
└─────────────────────────────────────────────────────────────┘
```

### Backend Layer (FastAPI)
```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
├─────────────────────────────────────────────────────────────┤
│  main.py (Application Entry)                               │
│  ├── CORS Middleware                                        │
│  ├── Lifespan Events                                        │
│  └── Global Exception Handler                               │
├─────────────────────────────────────────────────────────────┤
│  Routes Layer                                               │
│  ├── query.py (AI Chat Endpoints)                          │
│  ├── news.py (News Endpoints)                              │
│  ├── portfolio.py (Portfolio Endpoints)                    │
│  └── scheduler.py (Scheduler Management)                   │
├─────────────────────────────────────────────────────────────┤
│  Services Layer                                             │
│  ├── llm_service.py (LLM Integration)                      │
│  ├── rag_service.py (RAG Implementation)                   │
│  └── scheduler_service.py (RSS Scheduler)                  │
├─────────────────────────────────────────────────────────────┤
│  Utils Layer                                                │
│  ├── config.py (Configuration Management)                  │
│  └── logging.py (Logging Utilities)                        │
└─────────────────────────────────────────────────────────────┘
```

### Vector Services Layer
```
┌─────────────────────────────────────────────────────────────┐
│                Vector Services Layer                        │
├─────────────────────────────────────────────────────────────┤
│  vector_service_manager.py (Main Orchestrator)             │
│  ├── Service Initialization                                 │
│  ├── Document Management                                    │
│  ├── Search Coordination                                    │
│  └── System Status                                          │
├─────────────────────────────────────────────────────────────┤
│  Core Services                                              │
│  ├── embedding_service.py (Jina Embeddings)                │
│  ├── chroma_service.py (ChromaDB Integration)              │
│  ├── document_service.py (Document Metadata)               │
│  └── search_service.py (Hybrid Search)                     │
├─────────────────────────────────────────────────────────────┤
│  Data Storage                                               │
│  ├── ChromaDB (Vector Database)                            │
│  ├── Document Registry (JSON)                              │
│  └── Embedding Cache (Local)                               │
└─────────────────────────────────────────────────────────────┘
```

### Data Ingestion Layer
```
┌─────────────────────────────────────────────────────────────┐
│                Data Ingestion Pipeline                      │
├─────────────────────────────────────────────────────────────┤
│  fetch_news.py (RSS & NewsAPI)                             │
│  ├── RSS Feed Parser                                        │
│  ├── NewsAPI Integration                                    │
│  ├── Error Handling & Retry                                │
│  └── Data Validation                                        │
├─────────────────────────────────────────────────────────────┤
│  clean_data.py (Text Processing)                           │
│  ├── Text Normalization                                     │
│  ├── Content Extraction                                     │
│  ├── Text Chunking                                          │
│  └── Metadata Extraction                                    │
├─────────────────────────────────────────────────────────────┤
│  rss_config.py (Feed Configuration)                        │
│  ├── 24+ Financial RSS Feeds                               │
│  ├── Category Organization                                  │
│  ├── Feed Management                                        │
│  └── Testing Feeds                                          │
├─────────────────────────────────────────────────────────────┤
│  cron_jobs.py (Scheduling)                                 │
│  ├── Automated Fetching                                     │
│  ├── Batch Processing                                       │
│  ├── Error Recovery                                         │
│  └── Data Cleanup                                           │
└─────────────────────────────────────────────────────────────┘
```

## 🔗 Service Interactions

### API Request Flow
```
User Request → Frontend → API Gateway → Service Layer → Vector DB → Response
     │            │           │             │            │          │
     │            │           │             │            │          │
     ▼            ▼           ▼             ▼            ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│  User   │ │ React   │ │ FastAPI │ │ Service │ │ChromaDB │ │Response │
│ Query   │ │  UI     │ │ Router  │ │ Manager │ │ Vector  │ │ Format  │
└─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

### Data Ingestion Flow
```
RSS Feeds → Parser → Cleaner → Chunker → Embedder → Vector DB → Search Index
    │         │        │         │         │          │           │
    │         │        │         │         │          │           │
    ▼         ▼        ▼         ▼         ▼          ▼           ▼
┌─────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌────────┐ ┌────────┐ ┌────────┐
│RSS Data │ │Parse │ │Clean │ │Chunk │ │Embed   │ │Store   │ │Index   │
│Sources  │ │XML   │ │Text  │ │Text  │ │Vectors │ │Vectors │ │Search  │
└─────────┘ └──────┘ └──────┘ └──────┘ └────────┘ └────────┘ └────────┘
```

## 🗄️ Data Architecture

### Vector Database Schema
```
ChromaDB Collection: "finsight_documents"
├── Document ID (Primary Key)
├── Text Content (Chunked)
├── Embedding Vector (1024 dimensions)
├── Metadata
│   ├── source (RSS feed URL)
│   ├── category (business, markets, etc.)
│   ├── title (article title)
│   ├── published (publication date)
│   ├── url (article URL)
│   └── fetched_at (ingestion timestamp)
└── Search Index (HNSW)
```

### Document Registry
```json
{
  "documents": {
    "doc_123": {
      "id": "doc_123",
      "text": "Article content...",
      "metadata": {
        "source": "https://feeds.reuters.com/reuters/businessNews",
        "category": "business",
        "title": "Market Update",
        "published": "2024-01-01T10:00:00Z",
        "url": "https://reuters.com/article/123"
      },
      "embedding_generated": true,
      "created_at": "2024-01-01T10:05:00Z"
    }
  },
  "statistics": {
    "total_documents": 1500,
    "categories": {
      "business": 400,
      "markets": 350,
      "analysis": 300,
      "crypto": 200,
      "regional": 150,
      "commodities": 100
    }
  }
}
```

## 🔧 Configuration Architecture

### Environment Configuration
```
.env (Environment Variables)
├── JINA_API_KEY (Required)
├── NEWSAPI_KEY (Optional)
├── RSS_FETCH_INTERVAL_MINUTES
├── RSS_MAX_ARTICLES_PER_FEED
├── RSS_CATEGORIES
├── EMBEDDING_MODEL_NAME
├── CHROMA_PERSIST_DIR
└── DOCUMENT_STORAGE_DIR
```

### Scheduler Configuration
```json
{
  "scheduler": {
    "fetch_interval_minutes": 30,
    "max_articles_per_feed": 20,
    "categories_to_fetch": ["business", "markets", "analysis"],
    "enable_all_feeds": false,
    "batch_size": 50,
    "enable_on_startup": false,
    "cleanup_old_data": true,
    "max_data_age_days": 30
  }
}
```

## 🚀 Deployment Architecture

### Development Environment
```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │
│   (React Dev)   │◄──►│   (FastAPI)     │
│   Port: 3000    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Browser       │    │   Local Files   │
│   (Hot Reload)  │    │   (ChromaDB)    │
└─────────────────┘    └─────────────────┘
```

### Production Environment (Future)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   API Gateway   │    │   Microservices │
│   (Nginx)       │◄──►│   (Kong/AWS)    │◄──►│   (Docker)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CDN           │    │   Database      │    │   Monitoring    │
│   (Static)      │    │   (PostgreSQL)  │    │   (Prometheus)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📊 Performance Characteristics

### Vector Search Performance
- **Embedding Generation**: ~11.5 texts/second
- **Vector Dimensions**: 1024 (Jina v3)
- **Search Latency**: < 200ms for typical queries
- **Index Type**: HNSW (Hierarchical Navigable Small World)

### Data Ingestion Performance
- **RSS Feeds**: 24+ sources
- **Fetch Frequency**: Every 30 minutes (configurable)
- **Articles per Feed**: 20 (configurable)
- **Processing Rate**: ~50 articles/minute

### API Performance
- **Response Time**: < 2 seconds for typical queries
- **Concurrent Users**: 100+ (estimated)
- **Throughput**: 1000+ requests/hour (estimated)

---

**FinSightAI Architecture** - System Design Overview 🏗️
