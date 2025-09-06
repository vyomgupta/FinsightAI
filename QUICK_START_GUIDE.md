# FinSightAI - Quick Start Guide

## 🚀 Get Up and Running in 5 Minutes

This guide will help you quickly set up and run the FinSightAI platform on your local machine.

---

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed
- **Node.js 16+** installed
- **Git** installed
- A **Jina API key** (get one at [jina.ai](https://jina.ai))
- (Optional) A **NewsAPI key** (get one at [newsapi.org](https://newsapi.org))

---

## ⚡ Quick Setup

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd FinSightAI

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Create environment file
cp .env.example .env

# Edit .env file with your API keys
# Windows:
notepad .env
# macOS/Linux:
nano .env
```

**Required .env content:**
```env
JINA_API_KEY=your_jina_api_key_here
NEWSAPI_KEY=your_newsapi_key_here  # Optional
```

### 3. Initialize Database
```bash
# Initialize the vector database
python scripts/init_db.py

# (Optional) Seed with sample data
python scripts/seed_mock_data.py
```

### 4. Start the Backend
```bash
# Start the FastAPI server
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Start the Frontend (New Terminal)
```bash
# Navigate to web directory
cd web

# Install frontend dependencies
npm install

# Start the React development server
npm start
```

### 6. Access the Application
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

---

## 🎯 Quick Test

### Test the API
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test news endpoint
curl http://localhost:8000/news/latest?limit=5

# Test AI chat (requires data ingestion first)
curl -X POST http://localhost:8000/query/insights \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the latest market trends?"}'
```

### Test Data Ingestion
```bash
# Trigger manual RSS fetch
curl -X POST http://localhost:8000/scheduler/trigger

# Check scheduler status
curl http://localhost:8000/scheduler/status
```

---

## 🔧 One-Command Setup (Windows)

If you're on Windows, you can use the provided batch script:

```bash
# Run the full-stack setup script
start-full-stack.bat
```

This will:
1. Start the backend API server
2. Start the frontend development server
3. Open your browser to the application

---

## 📱 Using the Application

### 1. AI Chat Interface
- Navigate to the "AI Chat" tab
- Ask questions about financial markets, news, or investments
- The AI will search through news articles and provide intelligent responses

### 2. News & Insights
- Go to "News & Insights" tab
- Browse latest financial news from 24+ sources
- Filter by category (business, markets, analysis, crypto, etc.)
- Search for specific topics

### 3. Portfolio Management
- Navigate to "Portfolio" tab
- Add your investment holdings
- Track performance and gains/losses
- View portfolio analytics

### 4. Dashboard
- Check the "Dashboard" tab for system overview
- Monitor RSS scheduler status
- View system statistics

---

## 🛠️ Development Mode

### Backend Development
```bash
# Start with auto-reload
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
python -m pytest tests/

# Check API documentation
# Visit http://localhost:8000/docs
```

### Frontend Development
```bash
# Start with hot reload
cd web
npm start

# Run tests
npm test

# Build for production
npm run build
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# If port 8000 is busy, use a different port
uvicorn main:app --reload --port 8001

# If port 3000 is busy, React will automatically use 3001
```

#### 2. Jina API Key Issues
```
Error: Jina API key not found
Solution: Make sure JINA_API_KEY is set in your .env file
```

#### 3. Module Import Errors
```bash
# Make sure you're in the correct directory
cd FinSightAI

# Reinstall dependencies
pip install -r requirements.txt
```

#### 4. Frontend Build Issues
```bash
# Clear cache and reinstall
cd web
rm -rf node_modules package-lock.json
npm install
```

### Check System Status
```bash
# Backend health
curl http://localhost:8000/health

# Scheduler status
curl http://localhost:8000/scheduler/status

# Vector service status
curl http://localhost:8000/query/insights \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

---

## 📚 Next Steps

### 1. Explore the Code
- **Backend**: Check `api/` directory for FastAPI implementation
- **Frontend**: Explore `web/src/` for React components
- **Vector Services**: Review `vector-service/` for AI functionality
- **Data Ingestion**: Look at `data-ingest/` for RSS processing

### 2. Customize Configuration
- Edit `scheduler_config.json` for RSS settings
- Modify `data-ingest/rss_config.py` for news sources
- Update environment variables in `.env`

### 3. Add Features
- Create new API endpoints in `api/routes/`
- Add React components in `web/src/components/`
- Implement new services in `api/services/`

### 4. Run Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/real_end_to_end_test.py

# Run with coverage
python -m pytest tests/ --cov=api --cov=vector-service
```

---

## 🆘 Need Help?

### Documentation
- **Full Documentation**: `COMPREHENSIVE_DOCUMENTATION.md`
- **API Reference**: `API_REFERENCE.md`
- **Architecture**: `docs/architecture.md`

### Support
- Check the troubleshooting section above
- Review error messages in the console
- Check the API documentation at http://localhost:8000/docs

### Common Commands
```bash
# Check if services are running
curl http://localhost:8000/health
curl http://localhost:3000

# Restart services
# Stop with Ctrl+C, then restart

# Check logs
# Backend logs appear in the terminal
# Frontend logs appear in the browser console
```

---

## ✅ Success Checklist

- [ ] Python virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment variables configured (`.env` file)
- [ ] Database initialized (`python scripts/init_db.py`)
- [ ] Backend running (`uvicorn main:app --reload`)
- [ ] Frontend running (`npm start`)
- [ ] Application accessible at http://localhost:3000
- [ ] API documentation accessible at http://localhost:8000/docs
- [ ] Health check passing (`curl http://localhost:8000/health`)

---

**🎉 Congratulations! You now have FinSightAI running locally!**

**Next**: Explore the application, try the AI chat, and start building your financial intelligence platform!

---

**FinSightAI** - Quick Start Guide 🚀
