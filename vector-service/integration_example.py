#!/usr/bin/env python3
"""
Integration Example: Using Vector Services with FinSightAI News Data
Demonstrates how to integrate the vector service layer with news fetching
"""
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add the parent directory to the path so we can import from vector-service
sys.path.insert(0, str(Path(__file__).parent))

# Add the data-ingest directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "data-ingest"))

def integrate_news_with_vector_services():
    """
    Main integration function showing how to use vector services with news data
    """
    print("🚀 FinSightAI Vector Service Integration Example")
    print("=" * 80)
    
    try:
        # Import required services
        from vector_service_manager import get_default_vector_service_manager
        from fetch_news import fetch_news_from_rss, get_feeds_for_testing
        
        print("✅ Services imported successfully")
        
        # Initialize vector service manager
        print("\n🔄 Initializing Vector Service Manager...")
        manager = get_default_vector_service_manager(base_dir="./vector_integration")
        print("✅ Vector Service Manager initialized")
        
        # Get system status
        status = manager.get_system_status()
        print(f"📊 System Status:")
        print(f"   Embedding Model: {status['services']['embedding']['model_name']}")
        print(f"   Vector DB: {status['services']['chroma']['document_count']} documents")
        print(f"   Document Service: {status['services']['document']['total_documents']} documents")
        
        # Fetch news from RSS feeds
        print("\n📰 Fetching news from RSS feeds...")
        rss_feeds = get_feeds_for_testing()
        rss_urls = [feed.url for feed in rss_feeds]
        
        news_articles = fetch_news_from_rss(rss_urls, max_entries_per_feed=5)
        print(f"✅ Fetched {len(news_articles)} news articles")
        
        if not news_articles:
            print("⚠️  No news articles fetched. Creating sample data instead.")
            news_articles = create_sample_news_data()
        
        # Convert news articles to documents
        print("\n🔄 Converting news articles to documents...")
        documents = []
        
        for i, article in enumerate(news_articles):
            # Extract relevant fields
            title = article.get('title', f'News Article {i+1}')
            content = article.get('content', article.get('summary', 'No content available'))
            source = article.get('source', 'unknown')
            published = article.get('published', datetime.now().isoformat())
            
            # Clean and prepare content
            if content and len(content.strip()) > 50:  # Only include articles with substantial content
                # Determine category based on content
                category = determine_category(title, content)
                
                # Create document
                doc = {
                    'text': f"{title}\n\n{content}",
                    'metadata': {
                        'title': title,
                        'source': source,
                        'category': category,
                        'published': published,
                        'article_type': 'news',
                        'tags': extract_tags(title, content),
                        'word_count': len(content.split()),
                        'ingested_at': datetime.now().isoformat()
                    }
                }
                documents.append(doc)
        
        print(f"✅ Prepared {len(documents)} documents for ingestion")
        
        # Add documents to vector service
        print(f"\n📝 Adding documents to vector service...")
        start_time = datetime.now()
        
        doc_ids = manager.add_documents(
            documents=documents,
            generate_embeddings=True,
            add_to_vector_db=True
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"✅ Added {len(doc_ids)} documents in {processing_time:.2f} seconds")
        print(f"   Average: {processing_time/len(doc_ids):.2f} seconds per document")
        
        # Test search functionality
        print(f"\n🔍 Testing search functionality...")
        
        # Test different search queries
        search_queries = [
            "stock market",
            "cryptocurrency",
            "investment strategies",
            "economic news",
            "trading analysis"
        ]
        
        for query in search_queries:
            print(f"\n🔍 Searching for: '{query}'")
            results = manager.search(query, search_type="hybrid", n_results=3)
            
            if results:
                print(f"   Found {len(results)} results:")
                for j, result in enumerate(results[:2]):  # Show top 2 results
                    score = result.score
                    title = result.document.metadata.get('title', 'No title')
                    source = result.document.metadata.get('source', 'Unknown')
                    print(f"     {j+1}. [{score:.3f}] {title} (Source: {source})")
            else:
                print(f"   No results found")
        
        # Test category-based search
        print(f"\n🔍 Testing category-based search...")
        categories = ['business', 'markets', 'crypto', 'finance']
        
        for category in categories:
            results = manager.search_by_category(category, n_results=2)
            if results:
                print(f"   {category.capitalize()}: {len(results)} documents")
        
        # Test metadata filtering
        print(f"\n🔍 Testing metadata filtering...")
        filtered_results = manager.search(
            query="market",
            metadata_filters={'category': 'markets'},
            n_results=5
        )
        print(f"   Markets category + 'market' query: {len(filtered_results)} results")
        
        # Get updated system status
        print(f"\n📊 Updated System Status:")
        updated_status = manager.get_system_status()
        print(f"   Vector DB: {updated_status['services']['chroma']['document_count']} documents")
        print(f"   Document Service: {updated_status['services']['document']['total_documents']} documents")
        
        # Export system data
        print(f"\n📤 Exporting system data...")
        export_path = f"./vector_integration_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        export_success = manager.export_system_data(export_path)
        print(f"✅ System export: {export_success}")
        if export_success:
            print(f"   Export file: {export_path}")
        
        # Get search analytics
        print(f"\n📊 Search Analytics:")
        analytics = manager.search_service.get_search_analytics()
        print(f"   Total documents: {analytics['total_documents']}")
        print(f"   Categories: {list(analytics['categories'].keys())}")
        print(f"   Sources: {list(analytics['sources'].keys())}")
        
        print(f"\n🎉 Integration example completed successfully!")
        print(f"   You can now search through {len(doc_ids)} news articles using semantic search!")
        
        # Cleanup
        print(f"\n🧹 Cleaning up...")
        manager.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in integration: {e}")
        import traceback
        traceback.print_exc()
        return False


def determine_category(title, content):
    """Determine the category of a news article based on content"""
    text = f"{title} {content}".lower()
    
    if any(word in text for word in ['crypto', 'bitcoin', 'ethereum', 'blockchain']):
        return 'crypto'
    elif any(word in text for word in ['stock', 'market', 'trading', 'nasdaq', 's&p']):
        return 'markets'
    elif any(word in text for word in ['finance', 'banking', 'investment', 'portfolio']):
        return 'finance'
    elif any(word in text for word in ['economy', 'economic', 'gdp', 'inflation']):
        return 'economics'
    elif any(word in text for word in ['business', 'company', 'corporate', 'earnings']):
        return 'business'
    else:
        return 'general'


def extract_tags(title, content):
    """Extract relevant tags from article content"""
    text = f"{title} {content}".lower()
    tags = set()
    
    # Financial terms
    financial_terms = [
        'stocks', 'bonds', 'etfs', 'mutual funds', 'options', 'futures',
        'cryptocurrency', 'bitcoin', 'ethereum', 'blockchain', 'defi',
        'trading', 'investing', 'portfolio', 'diversification', 'risk management',
        'market analysis', 'technical analysis', 'fundamental analysis',
        'earnings', 'revenue', 'profit', 'loss', 'balance sheet', 'income statement'
    ]
    
    for term in financial_terms:
        if term in text:
            tags.add(term)
    
    # Add source-based tags
    if 'reuters' in text:
        tags.add('reuters')
    if 'bloomberg' in text:
        tags.add('bloomberg')
    if 'cnbc' in text:
        tags.add('cnbc')
    
    return list(tags)[:5]  # Limit to 5 tags


def create_sample_news_data():
    """Create sample news data for testing"""
    return [
        {
            'title': 'Stock Market Reaches New Highs Amid Economic Recovery',
            'content': 'The stock market has reached new record highs as economic indicators show strong recovery. Major indices including the S&P 500 and NASDAQ have posted significant gains, driven by strong corporate earnings and positive economic data.',
            'source': 'sample',
            'published': datetime.now().isoformat()
        },
        {
            'title': 'Bitcoin Surges Past $50,000 as Institutional Adoption Grows',
            'content': 'Cryptocurrency markets are experiencing a major rally with Bitcoin surpassing the $50,000 mark. This surge is attributed to increasing institutional adoption and growing interest from major financial institutions.',
            'source': 'sample',
            'published': datetime.now().isoformat()
        },
        {
            'title': 'Federal Reserve Announces New Monetary Policy Guidelines',
            'content': 'The Federal Reserve has announced updated monetary policy guidelines that will impact interest rates and economic growth. Analysts expect these changes to influence investment strategies across various asset classes.',
            'source': 'sample',
            'published': datetime.now().isoformat()
        }
    ]


def demonstrate_advanced_features():
    """Demonstrate advanced features of the vector service"""
    print("\n" + "=" * 80)
    print("🔬 ADVANCED FEATURES DEMONSTRATION")
    print("=" * 80)
    
    try:
        from vector_service_manager import get_default_vector_service_manager
        
        # Initialize manager
        manager = get_default_vector_service_manager(base_dir="./advanced_demo")
        
        # Add some specialized documents
        specialized_docs = [
            {
                'text': 'Advanced portfolio optimization techniques using modern portfolio theory and risk-adjusted returns.',
                'metadata': {
                    'category': 'finance',
                    'source': 'academic',
                    'complexity': 'advanced',
                    'tags': ['portfolio theory', 'optimization', 'risk management']
                }
            },
            {
                'text': 'Machine learning applications in algorithmic trading and market prediction models.',
                'metadata': {
                    'category': 'technology',
                    'source': 'research',
                    'complexity': 'advanced',
                    'tags': ['machine learning', 'algorithmic trading', 'prediction']
                }
            }
        ]
        
        doc_ids = manager.add_documents(specialized_docs)
        print(f"✅ Added {len(doc_ids)} specialized documents")
        
        # Test advanced search with metadata filters
        print(f"\n🔍 Advanced search with metadata filters...")
        
        # Search for advanced finance documents
        advanced_results = manager.search(
            query="portfolio optimization",
            metadata_filters={'complexity': 'advanced', 'category': 'finance'},
            n_results=5
        )
        print(f"   Advanced finance search: {len(advanced_results)} results")
        
        # Test similarity search
        print(f"\n🔍 Testing similarity search...")
        query_text = "How can I optimize my investment portfolio?"
        results = manager.search(query_text, search_type="semantic", n_results=3)
        print(f"   Similarity search for '{query_text}': {len(results)} results")
        
        # Test search suggestions
        print(f"\n💡 Testing search suggestions...")
        suggestions = manager.search_service.get_search_suggestions("port")
        print(f"   Suggestions for 'port': {suggestions}")
        
        # Cleanup
        manager.cleanup()
        print(f"✅ Advanced features demonstration completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in advanced features demo: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting FinSightAI Vector Service Integration Example")
    print("This example demonstrates how to integrate vector services with news data")
    print("=" * 80)
    
    # Run main integration
    success = integrate_news_with_vector_services()
    
    if success:
        # Run advanced features demo
        print(f"\n" + "=" * 80)
        print("Would you like to see advanced features? (y/n)")
        response = input().lower().strip()
        
        if response in ['y', 'yes']:
            demonstrate_advanced_features()
    
    print(f"\n🏁 Integration example completed!")
    print(f"   Check the generated files and directories for results")
    print(f"   You can now use the vector services in your FinSightAI application!")


