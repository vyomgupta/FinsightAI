#!/usr/bin/env python3
"""
Test Gemini API Integration
Quick test to verify the Gemini API key and client work correctly
"""
import os
import sys
from datetime import datetime

# Add project paths
sys.path.append('api/services')
sys.path.append('api/utils')

def test_direct_gemini_api():
    """Test direct Gemini API using google.genai"""
    print("🧪 Testing Direct Gemini API Integration")
    print("=" * 50)
    
    try:
        # Load API key from environment
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        
        print(f"✅ API Key loaded: {api_key[:10]}...")
        
        # Test the exact pattern from Google docs
        os.environ['GEMINI_API_KEY'] = api_key
        from google import genai
        from google.genai import types
        
        print("✅ Google GenAI imports successful")
        
        # Initialize client
        client = genai.Client()
        print("✅ Gemini client initialized")
        
        # Test basic generation (with thinking enabled by default)
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents="Explain how AI works in a few words"
        )
        
        print(f"✅ Basic API call successful!")
        print(f"📝 Response: {response.text}")
        
        # Test optimized generation (thinking disabled for speed/cost)
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking
        )
        
        response_optimized = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Explain how AI works in a few words",
            config=config
        )
        
        print(f"✅ Optimized API call successful!")
        print(f"📝 Optimized Response: {response_optimized.text}")
        print(f"💡 Note: Thinking disabled for faster responses and lower costs")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Please install: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_llm_service_integration():
    """Test the LLM service with Gemini"""
    print("\n🤖 Testing LLM Service Integration")
    print("=" * 50)
    
    try:
        from llm_service import create_llm_service
        
        # Create LLM service with Gemini as default
        config = {
            'default_provider': 'gemini',
            'api_keys': {
                'gemini': os.getenv('GEMINI_API_KEY')
            },
            'models': {
                'gemini': 'gemini-2.5-flash'
            }
        }
        
        llm_service = create_llm_service(config)
        print("✅ LLM service created")
        
        # Test service status
        status = llm_service.get_service_status()
        print(f"✅ Service status: {status}")
        
        # Test insight generation
        response = llm_service.generate_insights(
            query="What is artificial intelligence?",
            context="AI is a field of computer science focused on creating intelligent machines.",
            insight_type="general"
        )
        
        print(f"✅ Insight generation successful!")
        print(f"📝 Provider: {response.provider}")
        print(f"📝 Model: {response.model}")
        print(f"📝 Response: {response.content[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_rag_pipeline_with_gemini():
    """Test the complete RAG pipeline with Gemini"""
    print("\n🔄 Testing RAG Pipeline with Gemini")
    print("=" * 50)
    
    try:
        # Import test components
        sys.path.append('tests')
        from test_rag_llm_integration import MockVectorServiceManager
        from rag_service import RAGService
        from llm_service import create_llm_service
        
        # Create LLM service with Gemini
        llm_config = {
            'default_provider': 'gemini',
            'api_keys': {
                'gemini': os.getenv('GEMINI_API_KEY')
            },
            'models': {
                'gemini': 'gemini-2.5-flash'
            }
        }
        
        llm_service = create_llm_service(llm_config)
        
        # Create mock vector service with financial data
        mock_vector_manager = MockVectorServiceManager()
        mock_vector_manager.documents = [
            {
                'id': 'test1',
                'text': 'Apple Inc. reported strong quarterly earnings with revenue growth of 8% year-over-year.',
                'metadata': {'title': 'Apple Earnings', 'source': 'financial_news', 'category': 'earnings'}
            }
        ]
        
        # Create RAG service
        rag_service = RAGService(
            vector_service_manager=mock_vector_manager,
            llm_service=llm_service
        )
        
        print("✅ RAG service created with Gemini LLM")
        
        # Test end-to-end pipeline
        response = rag_service.generate_insights(
            query="What are Apple's latest earnings results?",
            retrieval_method="hybrid",
            insight_type="market_analysis",
            k=2
        )
        
        print(f"✅ RAG pipeline successful!")
        print(f"📊 Documents found: {response['retrieval']['documents_found']}")
        print(f"🤖 LLM Provider: {response['generation']['provider']}")
        print(f"🔬 Model: {response['generation']['model']}")
        print(f"⏱️ Processing time: {response['pipeline']['total_time']:.3f}s")
        print(f"📝 Insights preview: {response['insights'][:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🎯 Gemini API Integration Test Suite")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().isoformat()}")
    
    results = []
    
    # Test 1: Direct API
    results.append(test_direct_gemini_api())
    
    # Test 2: LLM Service
    results.append(test_llm_service_integration())
    
    # Test 3: RAG Pipeline
    results.append(test_rag_pipeline_with_gemini())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "Direct Gemini API",
        "LLM Service Integration", 
        "RAG Pipeline with Gemini"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n🏆 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Gemini integration is working correctly.")
        print("\n🚀 Next steps:")
        print("1. Run the demo: python demo_rag_llm.py")
        print("2. Start the API server: python api/main.py")
        print("3. Test the endpoints: /query/ask, /query/insights")
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
