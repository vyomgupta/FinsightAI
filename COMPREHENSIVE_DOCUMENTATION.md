# FinSightAI - Comprehensive Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Core Components](#core-components)
6. [API Documentation](#api-documentation)
7. [Configuration Guide](#configuration-guide)
8. [Setup & Installation](#setup--installation)
9. [Usage Guide](#usage-guide)
10. [Development Guide](#development-guide)
11. [Testing](#testing)
12. [Deployment](#deployment)
13. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

**FinSightAI** is a comprehensive financial intelligence platform that combines real-time news aggregation, portfolio management, and AI-powered vector search capabilities. The platform leverages modern AI technologies to provide intelligent insights into financial markets and news.

### Key Features
- **Real-time News Aggregation**: 24+ financial RSS feeds across 6 categories
- **AI-Powered Search**: Semantic search using Jina embeddings and ChromaDB
- **Portfolio Management**: Mock and real portfolio data handling
- **Interactive Web Interface**: Modern React-based frontend
- **RESTful API**: FastAPI-based backend with comprehensive endpoints
- **Scheduled Data Ingestion**: Automated RSS feed processing
- **Vector Database**: ChromaDB for efficient similarity search

---

## 🏗️ Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Data Layer    │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (ChromaDB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Components │    │   Services      │    │   Vector Store  │
│   - ChatBot     │    │   - LLM Service │    │   - Embeddings  │
│   - NewsView    │    │   - RAG Service │    │   - Documents   │
│   - Portfolio   │    │   - Scheduler   │    │   - Metadata    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow
1. **Data Ingestion**: RSS feeds → Data cleaning → Text chunking
2. **Vector Processing**: Text chunks → Jina embeddings → ChromaDB storage
3. **Query Processing**: User query → Embedding generation → Vector search
4. **Response Generation**: Search results → LLM processing → Formatted response

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104.0+
- **Language**: Python 3.8+
- **Vector Database**: ChromaDB 0.4.0+
- **Embeddings**: Jina embeddings v3 (1024 dimensions)
- **Data Processing**: Pandas, NumPy, scikit-learn
- **Web Scraping**: requests, beautifulsoup4, feedparser
- **Scheduling**: Custom scheduler with cron-like functionality

### Frontend
- **Framework**: React 18.2.0
- **Language**: TypeScript 4.9.5
- **UI Library**: Material-UI (MUI) 5.15.0
- **Charts**: Recharts 2.8.0, MUI X Charts 6.19.0
- **HTTP Client**: Axios 1.6.0
- **Routing**: React Router DOM 6.8.0

### AI/ML
- **Embeddings**: Jina embeddings v3
- **Vector Search**: ChromaDB with HNSW indexing
- **LLM Integration**: Google Generative AI
- **Text Processing**: LangChain, transformers

---

## 📁 Project Structure

```
FinSightAI/
├── 📁 api/                          # FastAPI Backend
│   ├── main.py                      # Main API entry point
│   ├── routes/                      # API route definitions
│   │   ├── news.py                  # News-related endpoints
│   │   ├── portfolio.py             # Portfolio endpoints
│   │   └── query.py                 # Query/chat endpoints
│   ├── services/                    # Business logic services
│   │   ├── llm_service.py           # LLM integration
│   │   ├── rag_service.py           # RAG implementation
│   │   └── scheduler_service.py     # RSS scheduler
│   └── utils/                       # Utility functions
│       ├── config.py                # Configuration management
│       └── logging.py               # Logging utilities
│
├── 📁 data-ingest/                  # Data Ingestion Pipeline
│   ├── fetch_news.py                # RSS and NewsAPI integration
│   ├── fetch_portfolio.py           # Portfolio data management
│   ├── clean_data.py                # Text cleaning and chunking
│   ├── rss_config.py                # RSS feed configuration
│   ├── cron_jobs.py                 # Scheduled data ingestion
│   └── utils.py                     # Utility functions
│
├── 📁 vector-service/               # Vector Database Services
│   ├── vector_service_manager.py    # Main service orchestrator
│   ├── embedding_service.py         # Jina embeddings integration
│   ├── chroma_service.py            # ChromaDB vector database
│   ├── document_service.py          # Document metadata management
│   ├── search_service.py            # Hybrid search capabilities
│   └── integration_example.py       # Integration examples
│
├── 📁 web/                          # React Frontend
│   ├── src/
│   │   ├── components/              # React components
│   │   │   ├── ChatBot.tsx          # AI chat interface
│   │   │   ├── NewsInsights.tsx     # News display component
│   │   │   ├── PortfolioView.tsx    # Portfolio management
│   │   │   └── Dashboard.tsx        # Main dashboard
│   │   ├── services/                # API client services
│   │   │   └── apiClient.ts         # HTTP client configuration
│   │   ├── App.tsx                  # Main app component
│   │   └── index.tsx                # App entry point
│   ├── package.json                 # Frontend dependencies
│   └── tsconfig.json                # TypeScript configuration
│
├── 📁 docs/                         # Documentation
│   ├── architecture.md              # System architecture
│   ├── api_spec.md                  # API specification
│   └── [other docs]                 # Additional documentation
│
├── 📁 tests/                        # Test Suite
│   ├── test_vector_service_manager.py
│   ├── real_end_to_end_test.py
│   └── [other tests]                # Additional test files
│
├── 📁 scripts/                      # Utility Scripts
│   ├── init_db.py                   # Database initialization
│   ├── seed_mock_data.py            # Mock data generation
│   └── cleanup_vectors.py           # Vector cleanup utilities
│
├── 📁 data/                         # Data Storage
│   ├── raw/                         # Raw ingested data
│   └── processed/                   # Processed and vectorized data
│
├── requirements.txt                 # Python dependencies
├── scheduler_config.json            # Scheduler configuration
└── README.md                        # Project overview
```

---

## 🔧 Core Components

### 1. Vector Service Manager (`vector-service/vector_service_manager.py`)
The central orchestrator for all vector-related operations.

**Key Responsibilities:**
- Initialize and manage all vector services
- Coordinate document addition and search operations
- Provide unified interface for vector operations
- Handle system status and health checks

**Key Methods:**
```python
# Add documents to the system
add_documents(documents: List[Dict], generate_embeddings: bool, add_to_vector_db: bool)

# Search for documents
search(query: str, search_type: str, n_results: int, metadata_filters: Dict)

# Get system status
get_system_status() -> Dict[str, Any]

# Export/import system data
export_system_data(export_path: str) -> bool
import_system_data(import_path: str, clear_existing: bool) -> bool
```

### 2. Data Ingestion Pipeline (`data-ingest/`)
Handles real-time data collection from various sources.

**Components:**
- **RSS Feeds**: 24+ financial news sources across 6 categories
- **NewsAPI Integration**: Real-time financial news aggregation
- **Data Cleaning**: Text normalization and chunking
- **Scheduled Processing**: Automated data ingestion

**Key Functions:**
```python
# Fetch news from RSS feeds
fetch_news_from_rss(rss_urls: List[str], max_entries_per_feed: int) -> List[Dict]

# Fetch news by category
fetch_news_by_category(category: str, max_entries_per_feed: int) -> List[Dict]

# Process and save articles
ingest_rss_and_save(rss_urls: List[str], filename: str, chunk: bool) -> Path
```

### 3. FastAPI Backend (`api/`)
RESTful API server providing endpoints for all platform functionality.

**Main Endpoints:**
- `/query/insights` - AI chat and query processing
- `/news/latest` - Latest news retrieval
- `/portfolio` - Portfolio management
- `/scheduler/*` - RSS scheduler management

**Key Features:**
- CORS enabled for frontend integration
- Comprehensive error handling
- Health check endpoints
- Scheduler management endpoints

### 4. React Frontend (`web/`)
Modern web interface built with React and Material-UI.

**Components:**
- **ChatBot**: AI-powered chat interface
- **NewsInsights**: News display and filtering
- **PortfolioView**: Portfolio management interface
- **Dashboard**: System overview and analytics

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
Currently no authentication required (development mode).

### Core Endpoints

#### 1. Query/Insights
```http
POST /query/insights
Content-Type: application/json

{
  "query": "What are the latest market trends?",
  "context": "optional context",
  "max_results": 10
}
```

**Response:**
```json
{
  "response": "AI-generated response based on vector search",
  "sources": [
    {
      "title": "Article Title",
      "url": "https://example.com",
      "relevance_score": 0.95
    }
  ],
  "metadata": {
    "search_time": "0.123s",
    "results_count": 5
  }
}
```

#### 2. News Endpoints
```http
GET /news/latest?category=business&limit=10
GET /news/search?query=bitcoin&limit=5
```

#### 3. Portfolio Endpoints
```http
GET /portfolio
POST /portfolio
PUT /portfolio/{portfolio_id}
DELETE /portfolio/{portfolio_id}
```

#### 4. Scheduler Management
```http
GET /scheduler/status
POST /scheduler/start
POST /scheduler/stop
POST /scheduler/trigger
PUT /scheduler/config
```

### Error Responses
```json
{
  "detail": "Error message",
  "error": "Detailed error information",
  "status_code": 400
}
```

---

## ⚙️ Configuration Guide

### Environment Variables
Create a `.env` file in the project root:

```env
# Jina API Configuration
JINA_API_KEY=your_jina_api_key_here

# NewsAPI Configuration (Optional)
NEWSAPI_KEY=your_newsapi_key_here

# RSS Scheduler Configuration
RSS_FETCH_INTERVAL_MINUTES=30
RSS_MAX_ARTICLES_PER_FEED=20
RSS_CATEGORIES=business,markets,analysis
RSS_ENABLE_ALL_FEEDS=false
RSS_BATCH_SIZE=50
RSS_ENABLE_ON_STARTUP=false
RSS_CLEANUP_OLD_DATA=true
RSS_MAX_DATA_AGE_DAYS=30

# Vector Service Configuration
EMBEDDING_MODEL_NAME=jina-embeddings-v3
EMBEDDING_MODEL_TYPE=jina
EMBEDDING_CACHE_DIR=./vector_services/embeddings
CHROMA_PERSIST_DIR=./vector_services/chroma_db
CHROMA_COLLECTION_NAME=finsight_documents
DOCUMENT_STORAGE_DIR=./vector_services/documents
```

### Scheduler Configuration (`scheduler_config.json`)
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

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Jina API key
- NewsAPI key (optional)

### Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd FinSightAI

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize the database
python scripts/init_db.py

# Start the API server
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# Navigate to web directory
cd web

# Install dependencies
npm install

# Start development server
npm start
```

### Full Stack Setup
```bash
# Use the provided batch script (Windows)
start-full-stack.bat

# Or start manually
# Terminal 1: Backend
cd api && uvicorn main:app --reload

# Terminal 2: Frontend
cd web && npm start
```

---

## 📖 Usage Guide

### 1. Starting the System
1. Ensure all environment variables are set
2. Start the backend API server
3. Start the frontend development server
4. Access the application at `http://localhost:3000`

### 2. Using the AI Chat
1. Navigate to the "AI Chat" tab
2. Enter your financial questions
3. The system will search through news articles and provide AI-generated responses
4. View source articles for more details

### 3. Managing News
1. Go to "News & Insights" tab
2. Browse latest financial news
3. Filter by category or search for specific topics
4. View detailed article information

### 4. Portfolio Management
1. Navigate to "Portfolio" tab
2. Add, edit, or remove portfolio items
3. View portfolio performance and analytics

### 5. RSS Scheduler Management
1. Use the API endpoints to manage the RSS scheduler
2. Start/stop automated data ingestion
3. Monitor scheduler status and statistics

---

## 🛠️ Development Guide

### Code Structure Guidelines
1. **Backend**: Follow FastAPI best practices
2. **Frontend**: Use TypeScript and Material-UI components
3. **Services**: Implement proper error handling and logging
4. **Tests**: Write comprehensive tests for all components

### Adding New Features
1. **Backend**: Add new routes in `api/routes/`
2. **Frontend**: Create new components in `web/src/components/`
3. **Services**: Implement business logic in `api/services/`
4. **Tests**: Add corresponding tests in `tests/`

### Database Schema
The system uses ChromaDB for vector storage with the following structure:
- **Collection**: `finsight_documents`
- **Documents**: Text chunks with metadata
- **Embeddings**: 1024-dimensional vectors (Jina v3)
- **Metadata**: Source, category, timestamp, etc.

### API Development
- Use FastAPI's automatic documentation at `/docs`
- Implement proper error handling
- Add comprehensive logging
- Follow RESTful conventions

---

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python tests/real_end_to_end_test.py
python tests/test_vector_service_manager.py

# Run with coverage
python -m pytest tests/ --cov=api --cov=vector-service --cov=data-ingest
```

### Test Categories
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Service integration testing
3. **End-to-End Tests**: Complete pipeline testing
4. **Performance Tests**: Load and performance testing

### Test Data
- Mock data available in `scripts/seed_mock_data.py`
- Real RSS feeds for integration testing
- Sample portfolios for testing

---

## 🚀 Deployment

### Production Considerations
1. **Environment Variables**: Set all required environment variables
2. **Database**: Configure persistent ChromaDB storage
3. **Logging**: Set up proper logging configuration
4. **Monitoring**: Implement health checks and monitoring
5. **Security**: Add authentication and authorization

### Docker Deployment (Future)
```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend Dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

### Environment-Specific Configuration
- **Development**: Local development with hot reload
- **Staging**: Production-like environment for testing
- **Production**: Optimized for performance and reliability

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Jina API Key Issues
```
Error: Jina API key not found
Solution: Set JINA_API_KEY environment variable
```

#### 2. ChromaDB Connection Issues
```
Error: ChromaDB connection failed
Solution: Check CHROMA_PERSIST_DIR path and permissions
```

#### 3. RSS Feed Fetching Issues
```
Error: RSS feed fetch failed
Solution: Check network connectivity and feed URLs
```

#### 4. Frontend Build Issues
```
Error: npm install failed
Solution: Clear node_modules and package-lock.json, then reinstall
```

### Debugging
1. **Backend**: Check logs in console or log files
2. **Frontend**: Use browser developer tools
3. **Vector Services**: Use system status endpoints
4. **Scheduler**: Check scheduler status and logs

### Performance Optimization
1. **Vector Search**: Optimize embedding generation and storage
2. **RSS Feeds**: Implement caching and rate limiting
3. **Frontend**: Use React optimization techniques
4. **Database**: Optimize ChromaDB configuration

---

## 📊 System Status

### Current Implementation Status
- ✅ **Backend API**: Fully implemented
- ✅ **Vector Services**: Production ready
- ✅ **Data Ingestion**: 24+ RSS feeds configured
- ✅ **Frontend**: Complete React application
- ✅ **Testing**: Comprehensive test suite
- ✅ **Documentation**: Complete documentation

### Performance Metrics
- **RSS Feeds**: 24 real feeds across 6 categories
- **Embedding Generation**: ~11.5 texts/second
- **Vector Dimensions**: 1024 (Jina embeddings v3)
- **Search Performance**: Hybrid search with semantic + text matching
- **Response Time**: < 2 seconds for typical queries

---

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards
- Follow Python PEP 8 for backend code
- Use TypeScript best practices for frontend
- Write comprehensive tests
- Update documentation as needed
- Use meaningful commit messages

---

## 📄 License

[Add your license information here]

---

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the troubleshooting section

---

**FinSightAI** - Transforming financial intelligence with AI-powered insights 🚀
