#!/usr/bin/env python3
"""
Test Real Jina Embeddings for FinSightAI
Tests the actual Jina embedding service with the provided API key
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the necessary paths to sys.path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "vector-service"))

def test_jina_api_key():
    """Test if Jina API key is properly set"""
    print("🔑 Testing Jina API Key")
    print("=" * 50)
    
    jina_api_key = os.getenv("JINA_API_KEY")
    if not jina_api_key:
        print("✗ JINA_API_KEY not set")
        return False
    
    print(f"✓ Jina API key is set")
    print(f"  Key starts with: {jina_api_key[:20]}...")
    print(f"  Key length: {len(jina_api_key)} characters")
    
    return True

def test_embedding_service():
    """Test the embedding service with real Jina API"""
    print("\n🤖 Testing Embedding Service")
    print("=" * 50)
    
    try:
        import embedding_service
        
        # Initialize the service
        embedding_service_instance = embedding_service.EmbeddingService()
        print("✓ Embedding service initialized successfully")
        
        # Get model info
        model_info = embedding_service_instance.get_model_info()
        print(f"✓ Model info retrieved:")
        print(f"  Model type: {model_info['model_type']}")
        print(f"  Model name: {model_info['model_name']}")
        print(f"  Embedding dimension: {model_info['embedding_dimension']}")
        
        return embedding_service_instance
        
    except Exception as e:
        print(f"✗ Embedding service test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_text_encoding():
    """Test encoding real financial text"""
    print("\n📝 Testing Text Encoding")
    print("=" * 50)
    
    try:
        import embedding_service
        
        # Initialize service
        embedding_service_instance = embedding_service.EmbeddingService()
        
        # Test texts
        test_texts = [
            "The stock market showed strong performance today with major indices up 2%.",
            "Technology stocks led the gains, with AI companies showing particular strength.",
            "Federal Reserve indicated potential interest rate cuts in coming months.",
            "Earnings season begins with several companies reporting better-than-expected results.",
            "Oil prices rose on supply concerns and geopolitical tensions in the Middle East."
        ]
        
        print(f"Testing encoding of {len(test_texts)} financial texts...")
        
        # Encode texts
        embeddings = embedding_service_instance.encode(test_texts)
        print(f"✓ Successfully encoded {len(embeddings)} texts")
        
        # Display embedding details
        for i, (text, embedding) in enumerate(zip(test_texts, embeddings)):
            print(f"\n  Text {i+1}: {text[:60]}...")
            print(f"    Embedding length: {len(embedding)} dimensions")
            print(f"    First 5 values: {embedding[:5]}")
            print(f"    Last 5 values: {embedding[-5:]}")
        
        return embeddings
        
    except Exception as e:
        print(f"✗ Text encoding test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_similarity_calculation():
    """Test similarity calculations between embeddings"""
    print("\n🔍 Testing Similarity Calculations")
    print("=" * 50)
    
    try:
        import embedding_service
        
        # Initialize service
        embedding_service_instance = embedding_service.EmbeddingService()
        
        # Test pairs of related and unrelated texts
        text_pairs = [
            ("The stock market rallied today.", "Stock prices increased significantly."),
            ("Oil prices rose on supply concerns.", "Technology stocks led market gains."),
            ("Federal Reserve policy affects markets.", "Central bank decisions impact trading."),
            ("Earnings reports beat expectations.", "Company profits exceeded analyst forecasts."),
            ("Cryptocurrency markets are volatile.", "Digital assets show price fluctuations.")
        ]
        
        print(f"Testing similarity between {len(text_pairs)} text pairs...")
        
        similarities = []
        for i, (text1, text2) in enumerate(text_pairs, 1):
            # Encode both texts
            embedding1 = embedding_service_instance.encode(text1)
            embedding2 = embedding_service_instance.encode(text2)
            
            # Calculate similarity
            similarity = embedding_service_instance.similarity(embedding1, embedding2)
            similarities.append(similarity)
            
            print(f"\n  Pair {i}:")
            print(f"    Text 1: {text1}")
            print(f"    Text 2: {text2}")
            print(f"    Similarity: {similarity:.4f}")
        
        # Calculate average similarity
        avg_similarity = sum(similarities) / len(similarities)
        print(f"\n✓ Average similarity across all pairs: {avg_similarity:.4f}")
        
        return similarities
        
    except Exception as e:
        print(f"✗ Similarity calculation test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_batch_processing():
    """Test batch processing capabilities"""
    print("\n📦 Testing Batch Processing")
    print("=" * 50)
    
    try:
        import embedding_service
        
        # Initialize service
        embedding_service_instance = embedding_service.EmbeddingService()
        
        # Create a larger batch of texts
        batch_texts = [
            f"Financial news article number {i} about market trends and investment strategies."
            for i in range(1, 21)  # 20 texts
        ]
        
        print(f"Testing batch encoding of {len(batch_texts)} texts...")
        
        # Time the batch processing
        import time
        start_time = time.time()
        
        embeddings = embedding_service_instance.encode(batch_texts)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✓ Successfully processed {len(embeddings)} texts in {processing_time:.2f} seconds")
        print(f"  Average time per text: {processing_time/len(embeddings):.3f} seconds")
        print(f"  Processing rate: {len(embeddings)/processing_time:.1f} texts/second")
        
        # Verify all embeddings have the same dimension
        dimensions = [len(emb) for emb in embeddings]
        unique_dimensions = set(dimensions)
        
        if len(unique_dimensions) == 1:
            print(f"✓ All embeddings have consistent dimension: {list(unique_dimensions)[0]}")
        else:
            print(f"⚠ Inconsistent embedding dimensions: {unique_dimensions}")
        
        return embeddings
        
    except Exception as e:
        print(f"✗ Batch processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_financial_document_embeddings():
    """Test embeddings with actual financial documents"""
    print("\n📊 Testing Financial Document Embeddings")
    print("=" * 50)
    
    try:
        import embedding_service
        
        # Initialize service
        embedding_service_instance = embedding_service.EmbeddingService()
        
        # Sample financial documents
        financial_docs = [
            {
                "title": "Market Analysis Report",
                "content": "The S&P 500 index closed at a record high today, driven by strong earnings from technology companies and positive economic data. Analysts expect continued growth in the coming quarter as corporate profits remain robust and consumer confidence stays elevated.",
                "category": "market_analysis"
            },
            {
                "title": "Federal Reserve Policy Update",
                "content": "The Federal Reserve maintained its current interest rate policy while signaling potential adjustments based on inflation trends. Market participants interpreted the statement as dovish, leading to a rally in rate-sensitive sectors including real estate and utilities.",
                "category": "policy_analysis"
            },
            {
                "title": "Earnings Season Preview",
                "content": "Q4 earnings season begins next week with major financial institutions reporting first. Expectations are high following strong economic indicators and consumer spending data. Technology and healthcare sectors are projected to lead growth.",
                "category": "earnings_analysis"
            }
        ]
        
        print(f"Testing embeddings for {len(financial_docs)} financial documents...")
        
        document_embeddings = []
        for i, doc in enumerate(financial_docs, 1):
            # Combine title and content
            full_text = f"{doc['title']}: {doc['content']}"
            
            # Generate embedding
            embedding = embedding_service_instance.encode(full_text)
            document_embeddings.append({
                "document": doc,
                "embedding": embedding,
                "text_length": len(full_text)
            })
            
            print(f"  ✓ Document {i}: {doc['title']}")
            print(f"    Text length: {len(full_text)} characters")
            print(f"    Embedding dimension: {len(embedding)}")
        
        # Test similarity between documents
        print(f"\n--- Testing Document Similarities ---")
        for i in range(len(document_embeddings)):
            for j in range(i + 1, len(document_embeddings)):
                doc1 = document_embeddings[i]
                doc2 = document_embeddings[j]
                
                similarity = embedding_service_instance.similarity(
                    doc1["embedding"], 
                    doc2["embedding"]
                )
                
                print(f"  {doc1['document']['title']} ↔ {doc2['document']['title']}")
                print(f"    Similarity: {similarity:.4f}")
        
        return document_embeddings
        
    except Exception as e:
        print(f"✗ Financial document embeddings test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_embedding_results(embeddings_data):
    """Save embedding test results"""
    print("\n💾 Saving Embedding Test Results")
    print("=" * 50)
    
    try:
        # Create results directory
        os.makedirs("data/processed", exist_ok=True)
        
        # Prepare results data
        results = {
            "test_timestamp": datetime.now().isoformat(),
            "jina_api_key_set": bool(os.getenv("JINA_API_KEY")),
            "embedding_service": "jina-embeddings-v3",
            "embedding_dimension": 1024,
            "tests_performed": [
                "API Key Validation",
                "Service Initialization", 
                "Text Encoding",
                "Similarity Calculation",
                "Batch Processing",
                "Financial Document Embeddings"
            ],
            "sample_embeddings": {
                "count": len(embeddings_data) if embeddings_data else 0,
                "dimension": 1024
            }
        }
        
        # Save to file
        results_path = "data/processed/embedding_test_results.json"
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Embedding test results saved to {results_path}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to save embedding results: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 FinSightAI Real Jina Embeddings Test")
    print("=" * 60)
    
    # Check environment
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"JINA_API_KEY set: {'Yes' if os.getenv('JINA_API_KEY') else 'No'}")
    
    # Run tests
    tests = [
        ("Jina API Key", test_jina_api_key),
        ("Embedding Service", test_embedding_service),
        ("Text Encoding", test_text_encoding),
        ("Similarity Calculation", test_similarity_calculation),
        ("Batch Processing", test_batch_processing),
        ("Financial Documents", test_financial_document_embeddings),
    ]
    
    results = {}
    embeddings_data = None
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_name == "Text Encoding":
                embeddings_data = test_func()
                results[test_name] = embeddings_data is not None
            elif test_name == "Financial Documents":
                doc_embeddings = test_func()
                results[test_name] = doc_embeddings is not None
            else:
                success = test_func()
                results[test_name] = success
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Save results
    save_embedding_results(embeddings_data)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Jina embeddings are working correctly.")
        print("\nThe system is ready to generate real embeddings for:")
        print("- Financial news articles")
        print("- Portfolio data")
        print("- Market analysis documents")
        print("- Any text content for vector search")
    else:
        print("⚠ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
