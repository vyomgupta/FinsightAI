#!/usr/bin/env python3
"""
Test script for Vector Service Layer
Tests all services individually and in combination
"""
import sys
import os
from pathlib import Path
import json
import time

# Add the parent directory to the path so we can import from vector-service
sys.path.insert(0, str(Path(__file__).parent))

def test_embedding_service():
    """Test the embedding service"""
    print("=" * 60)
    print("Testing Embedding Service")
    print("=" * 60)
    
    try:
        from embedding_service import get_default_embedding_service
        
        # Initialize service
        service = get_default_embedding_service()
        print(f"✅ Embedding service initialized")
        
        # Get model info
        model_info = service.get_model_info()
        print(f"📊 Model info: {model_info['model_type']} - {model_info['model_name']}")
        print(f"📏 Embedding dimension: {model_info['embedding_dimension']}")
        
        # Test encoding
        test_texts = [
            "This is a test sentence about finance.",
            "Another sentence about stock markets.",
            "A third sentence about investments."
        ]
        
        print(f"\n🔄 Testing text encoding...")
        start_time = time.time()
        embeddings = service.encode(test_texts)
        end_time = time.time()
        
        print(f"✅ Encoded {len(embeddings)} texts in {end_time - start_time:.2f}s")
        print(f"📊 Embedding shape: {len(embeddings)} x {len(embeddings[0])}")
        
        # Test similarity
        print(f"\n🔍 Testing similarity calculation...")
        sim1 = service.similarity(embeddings[0], embeddings[1])
        sim2 = service.similarity(embeddings[0], embeddings[2])
        sim3 = service.similarity(embeddings[1], embeddings[2])
        
        print(f"📊 Similarity scores:")
        print(f"   Finance vs Markets: {sim1:.4f}")
        print(f"   Finance vs Investments: {sim2:.4f}")
        print(f"   Markets vs Investments: {sim3:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing embedding service: {e}")
        return False


def test_jina_embeddings():
    """Test Jina embeddings specifically"""
    print("\n" + "=" * 60)
    print("Testing Jina Embeddings")
    print("=" * 60)
    
    try:
        from embedding_service import get_jina_embedding_service
        
        # Check if Jina API key is available
        jina_api_key = os.getenv("JINA_API_KEY")
        if not jina_api_key:
            print("⚠️  JINA_API_KEY not set, skipping Jina test")
            return True  # Not a failure, just skip
        
        # Initialize Jina service
        service = get_jina_embedding_service(api_key=jina_api_key)
        print(f"✅ Jina embedding service initialized")
        
        # Get model info
        model_info = service.get_model_info()
        print(f"📊 Model info: {model_info['model_type']} - {model_info['model_name']}")
        print(f"📏 Embedding dimension: {model_info['embedding_dimension']}")
        
        # Test encoding with multilingual texts
        test_texts = [
            "Financial markets are experiencing volatility.",
            "Los mercados financieros experimentan volatilidad.",
            "Die Finanzmärkte erleben Volatilität.",
            "金融市场正在经历波动。",
            "金融市場は変動を経験しています。"
        ]
        
        print(f"\n🔄 Testing multilingual text encoding...")
        start_time = time.time()
        embeddings = service.encode(test_texts)
        end_time = time.time()
        
        print(f"✅ Encoded {len(embeddings)} multilingual texts in {end_time - start_time:.2f}s")
        print(f"📊 Embedding shape: {len(embeddings)} x {len(embeddings[0])}")
        
        # Test cross-language similarity
        print(f"\n🔍 Testing cross-language similarity...")
        english_embedding = embeddings[0]
        languages = ["English", "Spanish", "German", "Chinese", "Japanese"]
        
        for i, (lang, embedding) in enumerate(zip(languages[1:], embeddings[1:])):
            similarity = service.similarity(english_embedding, embedding)
            print(f"   English ↔ {lang}: {similarity:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Jina embeddings: {e}")
        return False


def test_chroma_service():
    """Test the ChromaDB service"""
    print("\n" + "=" * 60)
    print("Testing ChromaDB Service")
    print("=" * 60)
    
    try:
        from chroma_service import create_chroma_service
        
        # Initialize service
        service = create_chroma_service(persist_directory="./test_chroma_db")
        print(f"✅ ChromaDB service initialized")
        
        # Test adding documents
        test_docs = [
            {
                'id': 'test_doc_1',
                'text': 'This is a test document about finance and investments.',
                'metadata': {'category': 'finance', 'source': 'test', 'tags': ['finance', 'investments']}
            },
            {
                'id': 'test_doc_2',
                'text': 'Another test document about stock market analysis.',
                'metadata': {'category': 'markets', 'source': 'test', 'tags': ['stocks', 'analysis']}
            },
            {
                'id': 'test_doc_3',
                'text': 'A third document about cryptocurrency trading strategies.',
                'metadata': {'category': 'crypto', 'source': 'test', 'tags': ['crypto', 'trading']}
            }
        ]
        
        print(f"\n📝 Testing document addition...")
        doc_ids = service.add_documents(test_docs)
        print(f"✅ Added {len(doc_ids)} documents")
        
        # Test search
        print(f"\n🔍 Testing search functionality...")
        results = service.search("finance", n_results=5)
        print(f"✅ Search returned {len(results['ids'][0])} results")
        
        # Test metadata filtering
        print(f"\n🔍 Testing metadata filtering...")
        filtered_results = service.search(
            "trading",
            n_results=5,
            where={'category': 'crypto'}
        )
        print(f"✅ Filtered search returned {len(filtered_results['ids'][0])} results")
        
        # Get collection info
        info = service.get_collection_info()
        print(f"📊 Collection info: {info['document_count']} documents")
        
        # Cleanup
        service.delete_collection()
        print(f"🧹 Cleaned up test collection")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ChromaDB service: {e}")
        return False


def test_document_service():
    """Test the document service"""
    print("\n" + "=" * 60)
    print("Testing Document Service")
    print("=" * 60)
    
    try:
        from document_service import create_document_service
        
        # Initialize service
        service = create_document_service(storage_dir="./test_documents")
        print(f"✅ Document service initialized")
        
        # Test adding documents
        test_docs = [
            {
                'text': 'This is a test document about finance and investments.',
                'metadata': {'category': 'finance', 'source': 'test', 'tags': ['finance', 'investments']}
            },
            {
                'text': 'Another test document about stock market analysis.',
                'metadata': {'category': 'markets', 'source': 'test', 'tags': ['stocks', 'analysis']}
            },
            {
                'text': 'A third document about cryptocurrency trading strategies.',
                'metadata': {'category': 'crypto', 'source': 'test', 'tags': ['crypto', 'trading']}
            }
        ]
        
        print(f"\n📝 Testing document addition...")
        added_docs = []
        for doc_data in test_docs:
            doc = service.add_document(
                text=doc_data['text'],
                metadata=doc_data['metadata']
            )
            added_docs.append(doc)
            print(f"   ✅ Added document: {doc.document_id}")
        
        # Test search
        print(f"\n🔍 Testing text search...")
        results = service.search_documents(query="finance")
        print(f"✅ Text search returned {len(results)} results")
        
        # Test metadata filtering
        print(f"\n🔍 Testing metadata filtering...")
        finance_docs = service.get_documents_by_category('finance')
        print(f"✅ Category filter returned {len(finance_docs)} finance documents")
        
        # Test metadata summary
        print(f"\n📊 Testing metadata summary...")
        summary = service.get_metadata_summary()
        print(f"✅ Summary: {summary['total_documents']} total documents")
        print(f"   Categories: {list(summary['categories'].keys())}")
        print(f"   Sources: {list(summary['sources'].keys())}")
        
        # Test export/import
        print(f"\n📤 Testing export/import...")
        export_path = "./test_documents_export.json"
        export_success = service.export_documents(export_path)
        print(f"✅ Export: {export_success}")
        
        # Cleanup
        import shutil
        if Path("./test_documents").exists():
            shutil.rmtree("./test_documents")
        if Path(export_path).exists():
            os.remove(export_path)
        print(f"🧹 Cleaned up test files")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing document service: {e}")
        return False


def test_search_service():
    """Test the search service"""
    print("\n" + "=" * 60)
    print("Testing Search Service")
    print("=" * 60)
    
    try:
        from embedding_service import get_default_embedding_service
        from chroma_service import create_chroma_service
        from document_service import create_document_service
        from search_service import create_search_service
        
        # Initialize all services
        print(f"🔄 Initializing services...")
        embedding_service = get_default_embedding_service()
        chroma_service = create_chroma_service(persist_directory="./test_search_chroma")
        document_service = create_document_service(storage_dir="./test_search_docs")
        
        search_service = create_search_service(
            embedding_service=embedding_service,
            chroma_service=chroma_service,
            document_service=document_service
        )
        print(f"✅ Search service initialized")
        
        # Add test documents
        print(f"\n📝 Adding test documents...")
        test_docs = [
            {
                'text': 'This is a comprehensive guide to personal finance and investment strategies.',
                'metadata': {'category': 'finance', 'source': 'test', 'title': 'Finance Guide'}
            },
            {
                'text': 'Advanced stock market analysis techniques for day trading and long-term investing.',
                'metadata': {'category': 'markets', 'source': 'test', 'title': 'Market Analysis'}
            },
            {
                'text': 'Cryptocurrency trading strategies and blockchain technology overview.',
                'metadata': {'category': 'crypto', 'source': 'test', 'title': 'Crypto Trading'}
            }
        ]
        
        for doc_data in test_docs:
            doc = document_service.add_document(
                text=doc_data['text'],
                metadata=doc_data['metadata']
            )
            
            # Generate embedding and add to vector DB
            embedding = embedding_service.encode(doc.text)
            chroma_doc = doc.to_chroma_format()
            chroma_service.add_documents([chroma_doc])
        
        print(f"✅ Added {len(test_docs)} test documents")
        
        # Test different search types
        print(f"\n🔍 Testing search types...")
        
        # Semantic search
        semantic_results = search_service.semantic_search("investment strategies", n_results=3)
        print(f"✅ Semantic search: {len(semantic_results)} results")
        
        # Text search
        text_results = search_service.text_search("trading", n_results=3)
        print(f"✅ Text search: {len(text_results)} results")
        
        # Hybrid search
        hybrid_results = search_service.hybrid_search("finance", n_results=3)
        print(f"✅ Hybrid search: {len(hybrid_results)} results")
        
        # Category search
        category_results = search_service.search_by_category("markets", query="trading", n_results=3)
        print(f"✅ Category search: {len(category_results)} results")
        
        # Get search analytics
        print(f"\n📊 Testing search analytics...")
        analytics = search_service.get_search_analytics()
        print(f"✅ Analytics: {analytics['total_documents']} documents")
        
        # Cleanup
        chroma_service.delete_collection()
        import shutil
        if Path("./test_search_chroma").exists():
            shutil.rmtree("./test_search_chroma")
        if Path("./test_search_docs").exists():
            shutil.rmtree("./test_search_docs")
        print(f"🧹 Cleaned up test files")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing search service: {e}")
        return False


def test_vector_service_manager():
    """Test the vector service manager"""
    print("\n" + "=" * 60)
    print("Testing Vector Service Manager")
    print("=" * 60)
    
    try:
        from vector_service_manager import get_default_vector_service_manager
        
        # Initialize manager
        print(f"🔄 Initializing vector service manager...")
        manager = get_default_vector_service_manager(base_dir="./test_vector_manager")
        print(f"✅ Vector service manager initialized")
        
        # Get system status
        print(f"\n📊 Getting system status...")
        status = manager.get_system_status()
        print(f"✅ System status retrieved")
        print(f"   Embedding model: {status['services']['embedding']['model_name']}")
        print(f"   Vector DB: {status['services']['chroma']['document_count']} documents")
        print(f"   Document service: {status['services']['document']['total_documents']} documents")
        
        # Test adding documents
        print(f"\n📝 Testing document addition...")
        test_docs = [
            {
                'text': 'This is a test document about finance and investments.',
                'metadata': {'category': 'finance', 'source': 'test', 'tags': ['finance', 'investments']}
            },
            {
                'text': 'Another test document about stock market analysis and trading strategies.',
                'metadata': {'category': 'markets', 'source': 'test', 'tags': ['stocks', 'trading', 'analysis']}
            }
        ]
        
        doc_ids = manager.add_documents(test_docs)
        print(f"✅ Added {len(doc_ids)} documents")
        
        # Test search
        print(f"\n🔍 Testing search functionality...")
        results = manager.search("finance", search_type="hybrid", n_results=5)
        print(f"✅ Search returned {len(results)} results")
        
        # Test category search
        print(f"\n🔍 Testing category search...")
        category_results = manager.search_by_category("finance", n_results=3)
        print(f"✅ Category search returned {len(category_results)} results")
        
        # Test system export
        print(f"\n📤 Testing system export...")
        export_path = "./test_system_export.json"
        export_success = manager.export_system_data(export_path)
        print(f"✅ System export: {export_success}")
        
        # Cleanup
        manager.cleanup()
        import shutil
        if Path("./test_vector_manager").exists():
            shutil.rmtree("./test_vector_manager")
        if Path(export_path).exists():
            os.remove(export_path)
        print(f"🧹 Cleaned up test files")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing vector service manager: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting Vector Service Layer Tests")
    print("=" * 80)
    
    test_results = []
    
    # Test individual services
    test_results.append(("Embedding Service", test_embedding_service()))
    test_results.append(("Jina Embeddings", test_jina_embeddings()))
    test_results.append(("ChromaDB Service", test_chroma_service()))
    test_results.append(("Document Service", test_document_service()))
    test_results.append(("Search Service", test_search_service()))
    test_results.append(("Vector Service Manager", test_vector_service_manager()))
    
    # Summary
    print("\n" + "=" * 80)
    print("🏁 TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(test_results)
    
    for service_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{service_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Vector Service Layer is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
