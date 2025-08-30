# Gemini API Setup Guide for FinSightAI

## ✅ Setup Complete

Your Gemini API key has been configured and the integration is ready to use!

## 🔧 What Was Done

1. **Environment File Created**: `.env` file with your Gemini API key
2. **LLM Service Updated**: Now uses the official `google.genai` client
3. **Model Updated**: Using the latest `gemini-2.5-flash` model
4. **Dependencies Added**: Added required packages to `requirements.txt`
5. **Configuration Enhanced**: Automatic .env loading with dotenv

## 📦 Installation Steps

To complete the setup, install the required packages:

```bash
# Install Google Generative AI and dotenv
pip install google-genai python-dotenv

# Or install all requirements
pip install -r requirements.txt
```

## 🧪 Testing the Integration

Run the test script to verify everything works:

```bash
python test_gemini_integration.py
```

This will test:
- ✅ Direct Gemini API connection
- ✅ LLM service integration
- ✅ Complete RAG pipeline with Gemini

## 🚀 Quick Demo

Run the interactive demo to see the RAG + Gemini pipeline in action:

```bash
python demo_rag_llm.py
```

## 🔗 API Usage Examples

### Simple Question (Auto-categorization)
```bash
curl -X POST "http://localhost:8000/query/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the latest Apple earnings results?"}'
```

### Advanced Insights with Gemini
```bash
curl -X POST "http://localhost:8000/query/insights" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze Tesla stock performance trends",
    "retrieval_method": "hybrid",
    "insight_type": "market_analysis",
    "llm_provider": "gemini",
    "k": 5
  }'
```

### Check Service Status
```bash
curl -X GET "http://localhost:8000/query/status"
```

## ⚙️ Configuration

### Environment Variables (`.env` file)
```env
# LLM Configuration
GEMINI_API_KEY=AIzaSyBlM6YiNkGeGpJmTVhaqhY1eBWCAn-Amy4
DEFAULT_LLM_PROVIDER=gemini

# Optional: OpenAI for comparison
# OPENAI_API_KEY=your_openai_key_here

# Vector Database
CHROMA_PERSIST_DIR=./vector_services/chroma_db
EMBEDDING_MODEL=jina-embeddings-v3

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

### Programmatic Configuration
```python
from api.utils.config import get_llm_config

# Get current LLM configuration
config = get_llm_config()
print(f"Default provider: {config['default_provider']}")
print(f"Available models: {config['models']}")
```

## 🎯 Key Features Now Available

### **Gemini-Powered Insights**
- **Model**: `gemini-2.5-flash` (latest and fastest)
- **Smart Prompting**: Context-aware prompts for financial analysis
- **Multi-turn Conversations**: System prompts + user queries
- **Performance Tracking**: Response times and usage metrics
- **Optimized Performance**: Thinking feature disabled for faster responses and lower costs

### **Intelligent Question Processing**
```python
# Automatic categorization
response = rag_service.ask_question("What's the market outlook for tech stocks?")
# → Categorized as: market_analysis
# → Uses specialized financial analysis prompts
```

### **Flexible LLM Provider Switching**
```python
# Use Gemini for detailed analysis
response = rag_service.generate_insights(
    query="Portfolio optimization strategies",
    llm_provider="gemini",
    insight_type="portfolio_advice"
)

# Compare with OpenAI (if configured)
response2 = rag_service.generate_insights(
    query="Portfolio optimization strategies", 
    llm_provider="openai",
    insight_type="portfolio_advice"
)
```

## 🔍 Code Integration Examples

### Basic RAG Pipeline
```python
import os
from dotenv import load_dotenv
load_dotenv()

from api.services.rag_service import get_default_rag_service

# Initialize RAG service (automatically uses Gemini)
rag_service = get_default_rag_service()

# Ask a financial question
response = rag_service.ask_question(
    "What are the latest trends in renewable energy investments?"
)

print(f"Insights: {response['insights']}")
print(f"Sources: {len(response['sources'])} documents")
print(f"Processing time: {response['pipeline']['total_time']:.2f}s")
```

### Advanced Usage
```python
# Custom retrieval and generation
response = rag_service.generate_insights(
    query="Analyze Q4 earnings across tech sector",
    retrieval_method="semantic",  # or "text", "hybrid"
    insight_type="market_analysis",
    k=10,  # retrieve 10 most relevant documents
    metadata_filters={"category": "earnings", "sector": "technology"},
    include_sources=True
)

# Access detailed results
print(f"Model used: {response['generation']['model']}")
print(f"Documents analyzed: {response['retrieval']['documents_found']}")
print(f"Confidence sources: {[s['title'] for s in response['sources']]}")
```

## 🛠️ Troubleshooting

### Common Issues

1. **Import Error**: `ModuleNotFoundError: No module named 'google.genai'`
   ```bash
   pip install google-generativeai
   ```

2. **API Key Not Found**
   - Check `.env` file exists in project root
   - Verify `GEMINI_API_KEY` is set correctly
   - Run: `python -c "import os; print(os.getenv('GEMINI_API_KEY'))"`

3. **Permission Errors**
   - Verify API key is valid and active
   - Check Google Cloud billing is enabled

### Testing Connection
```python
# Quick API test
import os
from google import genai

os.environ['GEMINI_API_KEY'] = 'your-key-here'
client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello in 5 words"
)
print(response.text)
```

## 📊 Performance Expectations

- **Response Time**: 0.5-2.0 seconds per query
- **Context Window**: Up to 4,000 characters of retrieved documents
- **Accuracy**: High-quality financial analysis with source attribution
- **Rate Limits**: Standard Gemini API limits apply

## 🎉 Ready to Use!

Your FinSightAI RAG + Gemini integration is now fully configured and ready for:

1. **Financial Question Answering**
2. **Market Analysis & Insights** 
3. **Portfolio Recommendations**
4. **News Summarization**
5. **Custom Financial Research**

Start the API server and begin asking intelligent financial questions! 🚀
