#!/usr/bin/env python3
"""
Quick Gemini API Test
Test the real Gemini API integration with a simple financial question
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project paths
sys.path.append('api/services')
sys.path.append('api/utils')

def test_real_gemini_api():
    """Test real Gemini API with a financial question"""
    print("🧪 Testing Real Gemini API Integration")
    print("=" * 50)
    
    try:
        # Test direct API call
        print("1. Testing Direct Gemini API...")
        
        from google import genai
        from google.genai import types
        
        # Initialize client (automatically picks up GEMINI_API_KEY)
        client = genai.Client()
        
        # Test with thinking disabled (faster, cheaper)
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="What are the key factors affecting stock market performance?",
            config=config
        )
        
        print(f"✅ Direct API Success!")
        print(f"📝 Response: {response.text[:200]}...")
        
        # Test our LLM service
        print("\n2. Testing LLM Service Integration...")
        
        from llm_service import create_llm_service
        
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
        
        llm_response = llm_service.generate_insights(
            query="Analyze current market conditions",
            context="Recent economic data shows inflation cooling to 3.1%. The Federal Reserve is considering rate cuts.",
            insight_type="market_analysis"
        )
        
        print(f"✅ LLM Service Success!")
        print(f"📝 Provider: {llm_response.provider}")
        print(f"📝 Model: {llm_response.model}")
        print(f"📝 Response: {llm_response.content[:200]}...")
        print(f"⏱️ Response Time: {llm_response.response_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_real_gemini_api()
    
    if success:
        print("\n🎉 Gemini API integration is working perfectly!")
        print("✅ Ready for production use")
    else:
        print("\n❌ There was an issue with the integration")
        print("💡 Check your API key and network connection")
