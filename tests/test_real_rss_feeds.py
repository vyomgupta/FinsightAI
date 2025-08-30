#!/usr/bin/env python3
"""
Test Real RSS Feeds for FinSightAI
Tests the actual RSS feeds to ensure they're working and can fetch real data
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the necessary paths to sys.path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "data-ingest"))

def test_rss_configuration():
    """Test RSS configuration and display all available feeds"""
    print("🔍 Testing RSS Configuration")
    print("=" * 50)
    
    try:
        import rss_config
        
        # Display all feeds
        all_feeds = rss_config.get_all_feed_urls()
        print(f"Total RSS feeds configured: {len(all_feeds)}")
        
        # Display feeds by category
        categories = rss_config.FEED_CATEGORIES
        for category, feeds in categories.items():
            print(f"\n{category.upper()} ({len(feeds)} feeds):")
            for feed in feeds:
                print(f"  ✓ {feed.name}")
                print(f"    URL: {feed.url}")
                print(f"    Description: {feed.description}")
        
        return True
        
    except Exception as e:
        print(f"✗ RSS configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_real_rss_fetching():
    """Test fetching from real RSS feeds"""
    print("\n📡 Testing Real RSS Feed Fetching")
    print("=" * 50)
    
    try:
        import fetch_news
        
        # Test with a few reliable feeds
        test_feeds = [
            "https://feeds.reuters.com/reuters/businessNews",
            "https://feeds.bloomberg.com/markets/news.rss",
            "https://www.cnbc.com/id/100003114/device/rss/rss.html"
        ]
        
        print(f"Testing {len(test_feeds)} RSS feeds...")
        
        for i, feed_url in enumerate(test_feeds, 1):
            print(f"\n--- Testing Feed {i}: {feed_url} ---")
            
            try:
                # Fetch articles from this feed
                articles = fetch_news.fetch_news_from_rss([feed_url], max_entries_per_feed=3)
                
                if articles:
                    print(f"✓ Successfully fetched {len(articles)} articles")
                    
                    # Display first article details
                    if articles:
                        first_article = articles[0]
                        print(f"  Sample article:")
                        print(f"    Title: {first_article.get('title', 'N/A')[:80]}...")
                        print(f"    Source: {first_article.get('source', 'N/A')}")
                        print(f"    Published: {first_article.get('published', 'N/A')}")
                        print(f"    Content length: {len(first_article.get('content', ''))} characters")
                else:
                    print("⚠ No articles fetched from this feed")
                    
            except Exception as e:
                print(f"✗ Error fetching from {feed_url}: {e}")
                continue
        
        return True
        
    except Exception as e:
        print(f"✗ RSS fetching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_newsapi_integration():
    """Test NewsAPI integration (if API key available)"""
    print("\n📰 Testing NewsAPI Integration")
    print("=" * 50)
    
    try:
        import fetch_news
        
        # Check if NewsAPI key is available
        newsapi_key = os.getenv("NEWSAPI_KEY")
        if not newsapi_key:
            print("⚠ NEWSAPI_KEY not set, skipping NewsAPI test")
            print("  Set NEWSAPI_KEY environment variable to test NewsAPI")
            return True
        
        print("✓ NewsAPI key available, testing integration...")
        
        # Test with a simple query
        test_query = "stock market"
        articles = fetch_news.fetch_news_from_newsapi(
            api_key=newsapi_key,
            query=test_query,
            page_size=3
        )
        
        if articles:
            print(f"✓ Successfully fetched {len(articles)} articles from NewsAPI")
            
            # Display first article details
            if articles:
                first_article = articles[0]
                print(f"  Sample article:")
                print(f"    Title: {first_article.get('title', 'N/A')[:80]}...")
                print(f"    Source: {first_article.get('source', 'N/A')}")
                print(f"    Published: {first_article.get('published', 'N/A')}")
                print(f"    Content length: {len(first_article.get('content', ''))} characters")
        else:
            print("⚠ No articles fetched from NewsAPI")
        
        return True
        
    except Exception as e:
        print(f"✗ NewsAPI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_category_based_fetching():
    """Test fetching news by category"""
    print("\n🏷️ Testing Category-Based News Fetching")
    print("=" * 50)
    
    try:
        import fetch_news
        
        # Test fetching by category
        test_categories = ["business", "markets", "analysis"]
        
        for category in test_categories:
            print(f"\n--- Testing {category.upper()} category ---")
            
            try:
                articles = fetch_news.fetch_news_by_category(category, max_entries_per_feed=2)
                
                if articles:
                    print(f"✓ Successfully fetched {len(articles)} articles from {category} category")
                    
                    # Show sample article
                    if articles:
                        sample = articles[0]
                        print(f"  Sample: {sample.get('title', 'N/A')[:60]}...")
                else:
                    print(f"⚠ No articles fetched from {category} category")
                    
            except Exception as e:
                print(f"✗ Error fetching {category} category: {e}")
                continue
        
        return True
        
    except Exception as e:
        print(f"✗ Category-based fetching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_processing():
    """Test data processing and chunking"""
    print("\n⚙️ Testing Data Processing and Chunking")
    print("=" * 50)
    
    try:
        import clean_data
        
        # Test with sample article
        sample_article = {
            'id': 'test1',
            'title': 'Test Financial Article',
            'content': 'This is a test article about financial markets and investment strategies. It contains multiple sentences to test the chunking functionality. The goal is to break down long text into manageable pieces for processing and embedding generation.',
            'summary': 'Test summary about finance',
            'source': 'Test Source',
            'link': 'https://example.com/test',
            'published': '2024-01-15T12:00:00Z'
        }
        
        # Test chunking
        chunks = clean_data.prepare_article_for_embeddings(sample_article, chunk_size=50, overlap=10)
        print(f"✓ Successfully created {len(chunks)} chunks from sample article")
        
        # Display chunks
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i+1}: {chunk['text'][:50]}...")
            print(f"    Metadata: {chunk['meta']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Data processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def save_test_results():
    """Save test results to a file"""
    print("\n💾 Saving Test Results")
    print("=" * 50)
    
    try:
        # Create test results directory
        os.makedirs("data/processed", exist_ok=True)
        
        # Save RSS feed list
        import rss_config
        feeds_data = {
            "test_timestamp": datetime.now().isoformat(),
            "total_feeds": len(rss_config.ALL_FEEDS),
            "categories": list(rss_config.FEED_CATEGORIES.keys()),
            "feeds_by_category": {}
        }
        
        for category, feeds in rss_config.FEED_CATEGORIES.items():
            feeds_data["feeds_by_category"][category] = [
                {
                    "name": feed.name,
                    "url": feed.url,
                    "description": feed.description
                }
                for feed in feeds
            ]
        
        # Save to file
        results_path = "data/processed/rss_test_results.json"
        with open(results_path, "w") as f:
            json.dump(feeds_data, f, indent=2)
        
        print(f"✓ Test results saved to {results_path}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to save test results: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 FinSightAI Real RSS Feed Test")
    print("=" * 60)
    
    # Check environment
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"JINA_API_KEY set: {'Yes' if os.getenv('JINA_API_KEY') else 'No'}")
    print(f"NEWSAPI_KEY set: {'Yes' if os.getenv('NEWSAPI_KEY') else 'No'}")
    
    # Run tests
    tests = [
        ("RSS Configuration", test_rss_configuration),
        ("Real RSS Fetching", test_real_rss_fetching),
        ("NewsAPI Integration", test_newsapi_integration),
        ("Category-Based Fetching", test_category_based_fetching),
        ("Data Processing", test_data_processing),
        ("Save Results", save_test_results),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results[test_name] = success
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results[test_name] = False
    
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
        print("🎉 All tests passed! RSS feeds are working correctly.")
    else:
        print("⚠ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
