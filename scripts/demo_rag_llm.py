#!/usr/bin/env python3
"""
Demo Script for RAG + LLM Integration in FinSightAI
Shows the complete pipeline from query to insights generation
"""
import os
import sys
import json
import logging
from datetime import datetime

# Add project paths
sys.path.append('api/services')
sys.path.append('api/utils')
sys.path.append('vector-service')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def setup_mock_data():
    """Set up mock data for demonstration"""
    mock_documents = [
        {
            'id': 'doc1',
            'text': 'Apple Inc. reported record quarterly earnings with revenue of $123.9 billion, up 8% year-over-year. The iPhone segment contributed $69.7 billion, showing strong demand despite market challenges.',
            'metadata': {
                'title': 'Apple Q4 2024 Earnings Beat Expectations',
                'source': 'financial_news',
                'category': 'earnings',
                'published': '2024-02-01T09:00:00Z',
                'sector': 'technology'
            }
        },
        {
            'id': 'doc2',
            'text': 'Tesla stock surged 12% in after-hours trading following the announcement of record vehicle deliveries for Q4 2024. The company delivered 484,507 vehicles, exceeding analyst estimates of 473,000.',
            'metadata': {
                'title': 'Tesla Delivers Record Vehicles in Q4',
                'source': 'market_news',
                'category': 'automotive',
                'published': '2024-01-02T16:30:00Z',
                'sector': 'automotive'
            }
        },
        {
            'id': 'doc3',
            'text': 'The Federal Reserve signaled potential interest rate cuts in the second half of 2024, citing cooling inflation data. The latest CPI reading came in at 3.1%, down from the previous month.',
            'metadata': {
                'title': 'Fed Hints at Rate Cuts as Inflation Cools',
                'source': 'economic_news',
                'category': 'monetary_policy',
                'published': '2024-01-15T14:00:00Z',
                'sector': 'economics'
            }
        },
        {
            'id': 'doc4',
            'text': 'Portfolio diversification remains crucial for risk management. Financial advisors recommend allocating 60% to stocks, 30% to bonds, and 10% to alternative investments for moderate risk profiles.',
            'metadata': {
                'title': 'Investment Portfolio Best Practices',
                'source': 'investment_advice',
                'category': 'portfolio_management',
                'published': '2024-01-10T10:00:00Z',
                'sector': 'finance'
            }
        },
        {
            'id': 'doc5',
            'text': 'Technical analysis shows strong support for the S&P 500 at 4,800 level. RSI indicators suggest the market is neither overbought nor oversold, with potential for continued upward momentum.',
            'metadata': {
                'title': 'S&P 500 Technical Analysis Update',
                'source': 'market_analysis',
                'category': 'technical_analysis',
                'published': '2024-01-20T11:30:00Z',
                'sector': 'markets'
            }
        }
    ]
    
    return mock_documents


def create_mock_rag_service():
    """Create a mock RAG service for demonstration"""
    try:
        # Import required modules
        from rag_service import RAGService
        from tests.test_rag_llm_integration import MockVectorServiceManager, MockLLMService
        
        # Set up mock data
        mock_documents = setup_mock_data()
        
        # Create enhanced mock services
        mock_vector_manager = MockVectorServiceManager()
        mock_vector_manager.documents = mock_documents
        
        mock_llm_service = MockLLMService()
        
        # Create RAG service
        rag_service = RAGService(
            vector_service_manager=mock_vector_manager,
            llm_service=mock_llm_service
        )
        
        logger.info("Mock RAG service created successfully")
        return rag_service
        
    except Exception as e:
        logger.error(f"Failed to create mock RAG service: {e}")
        return None


def demo_retrieval_only():
    """Demonstrate document retrieval without LLM generation"""
    print("\n" + "="*60)
    print("🔍 DEMO 1: DOCUMENT RETRIEVAL ONLY")
    print("="*60)
    
    rag_service = create_mock_rag_service()
    if not rag_service:
        print("❌ Failed to create RAG service")
        return
    
    query = "Apple earnings performance"
    print(f"Query: {query}")
    
    # Retrieve documents
    retrieval_result = rag_service.retrieve_context(
        query=query,
        k=3,
        retrieval_method="hybrid"
    )
    
    print(f"\n📊 Results:")
    print(f"  • Documents found: {retrieval_result.total_retrieved}")
    print(f"  • Retrieval method: {retrieval_result.retrieval_method}")
    print(f"  • Context length: {len(retrieval_result.get_context_text())} characters")
    
    print(f"\n📄 Retrieved Documents:")
    for i, result in enumerate(retrieval_result.search_results[:3], 1):
        print(f"  {i}. Score: {result.score:.3f}")
        print(f"     Title: {result.document.metadata.get('title', 'No title')}")
        print(f"     Excerpt: {result.document.text[:100]}...")
        print()


def demo_end_to_end_pipeline():
    """Demonstrate complete RAG pipeline with LLM generation"""
    print("\n" + "="*60)
    print("🤖 DEMO 2: END-TO-END RAG PIPELINE")
    print("="*60)
    
    rag_service = create_mock_rag_service()
    if not rag_service:
        print("❌ Failed to create RAG service")
        return
    
    query = "What are the latest trends in technology stocks?"
    print(f"Query: {query}")
    
    # Generate insights
    response = rag_service.generate_insights(
        query=query,
        retrieval_method="hybrid",
        insight_type="market_analysis",
        k=3,
        include_sources=True
    )
    
    print(f"\n🎯 AI Insights:")
    print(f"  {response['insights']}")
    
    print(f"\n📊 Pipeline Metrics:")
    print(f"  • Documents retrieved: {response['retrieval']['documents_found']}")
    print(f"  • LLM provider: {response['generation']['provider']}")
    print(f"  • Processing time: {response['pipeline']['total_time']:.3f} seconds")
    print(f"  • Status: {response['pipeline']['status']}")
    
    if response.get('sources'):
        print(f"\n📚 Source Documents:")
        for i, source in enumerate(response['sources'][:3], 1):
            print(f"  {i}. {source['title']} (Score: {source['score']:.3f})")
            print(f"     {source['excerpt']}")
            print()


def demo_question_categorization():
    """Demonstrate automatic question categorization"""
    print("\n" + "="*60)
    print("🎯 DEMO 3: AUTOMATIC QUESTION CATEGORIZATION")
    print("="*60)
    
    rag_service = create_mock_rag_service()
    if not rag_service:
        print("❌ Failed to create RAG service")
        return
    
    test_questions = [
        "What's the latest market trend analysis?",
        "How should I diversify my investment portfolio?",
        "What are the recent news about Tesla?",
        "Explain the concept of compound interest"
    ]
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        
        response = rag_service.ask_question(question, k=2)
        
        insight_type = response['generation']['insight_type']
        docs_found = response['retrieval']['documents_found']
        
        print(f"  → Categorized as: {insight_type}")
        print(f"  → Documents found: {docs_found}")
        print(f"  → Insight: {response['insights'][:150]}...")


def demo_different_retrieval_methods():
    """Demonstrate different retrieval methods"""
    print("\n" + "="*60)
    print("⚙️ DEMO 4: RETRIEVAL METHODS COMPARISON")
    print("="*60)
    
    rag_service = create_mock_rag_service()
    if not rag_service:
        print("❌ Failed to create RAG service")
        return
    
    query = "Federal Reserve interest rate policy"
    methods = ["semantic", "text", "hybrid"]
    
    print(f"Query: {query}")
    
    for method in methods:
        print(f"\n🔍 Method: {method}")
        
        response = rag_service.generate_insights(
            query=query,
            retrieval_method=method,
            k=2
        )
        
        print(f"  • Documents found: {response['retrieval']['documents_found']}")
        print(f"  • Processing time: {response['pipeline']['total_time']:.3f}s")
        print(f"  • Insight preview: {response['insights'][:100]}...")


def demo_service_status():
    """Demonstrate service status and capabilities"""
    print("\n" + "="*60)
    print("📊 DEMO 5: SERVICE STATUS & CAPABILITIES")
    print("="*60)
    
    rag_service = create_mock_rag_service()
    if not rag_service:
        print("❌ Failed to create RAG service")
        return
    
    try:
        status = rag_service.get_service_status()
        
        print("🚀 RAG Service Status:")
        rag_status = status.get('rag_service', {})
        print(f"  • Status: {rag_status.get('status', 'unknown')}")
        print(f"  • Retriever: {rag_status.get('components', {}).get('retriever', 'unknown')}")
        print(f"  • LLM Generator: {rag_status.get('components', {}).get('llm_generator', 'unknown')}")
        
        capabilities = status.get('pipeline_capabilities', {})
        if capabilities:
            print(f"\n⚡ Capabilities:")
            print(f"  • End-to-end generation: {capabilities.get('end_to_end_generation', False)}")
            print(f"  • Supported insight types: {', '.join(capabilities.get('supported_insight_types', []))}")
            print(f"  • Supported retrieval methods: {', '.join(capabilities.get('supported_retrieval_methods', []))}")
            print(f"  • Auto question categorization: {capabilities.get('auto_question_categorization', False)}")
        
        vector_status = status.get('vector_services', {})
        if vector_status:
            doc_service = vector_status.get('services', {}).get('document', {})
            print(f"\n💾 Vector Database:")
            print(f"  • Total documents: {doc_service.get('total_documents', 0)}")
            
    except Exception as e:
        logger.error(f"Error getting service status: {e}")


def main():
    """Run all demonstrations"""
    print("🎉 FinSightAI RAG + LLM Integration Demo")
    print("=" * 60)
    print("This demo showcases the complete RAG pipeline:")
    print("• Document retrieval from vector database")
    print("• Semantic, text, and hybrid search methods")
    print("• LLM-powered insight generation")
    print("• Automatic question categorization")
    print("• Performance metrics and monitoring")
    
    try:
        # Run all demos
        demo_retrieval_only()
        demo_end_to_end_pipeline()
        demo_question_categorization()
        demo_different_retrieval_methods()
        demo_service_status()
        
        print("\n" + "="*60)
        print("✅ Demo completed successfully!")
        print("="*60)
        print("\n🚀 Next Steps:")
        print("1. Set up API keys (OPENAI_API_KEY or GEMINI_API_KEY)")
        print("2. Ingest real financial data using data-ingest scripts")
        print("3. Start the API server: python api/main.py")
        print("4. Test endpoints: /query/ask, /query/insights, /query/retrieve")
        print("5. Integrate with frontend applications")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo encountered an error: {e}")


if __name__ == "__main__":
    main()
