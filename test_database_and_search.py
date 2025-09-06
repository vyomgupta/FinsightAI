#!/usr/bin/env python3
"""
Database and Search Test Script for FinSightAI

This script will:
1. Check what data currently exists in the database
2. Test the search functionality
3. Optionally populate test data if database is empty
4. Demonstrate different search types (semantic, text, hybrid)
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project paths to sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "vector-service"))
sys.path.insert(0, str(project_root / "api"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseTester:
    """Test and inspect the FinSightAI database and search functionality"""
    
    def __init__(self):
        """Initialize the database tester"""
        self.vector_manager = None
        self.test_results = {
            'database_status': {},
            'search_tests': {},
            'errors': [],
            'timestamp': datetime.now().isoformat()
        }
        
    def initialize_vector_service(self) -> bool:
        """Initialize the vector service manager"""
        try:
            from vector_service_manager import VectorServiceManager
            
            logger.info("Initializing Vector Service Manager...")
            self.vector_manager = VectorServiceManager(base_dir="./vector_services")
            logger.info("✅ Vector Service Manager initialized successfully")
            return True
            
        except Exception as e:
            error_msg = f"❌ Failed to initialize Vector Service Manager: {e}"
            logger.error(error_msg)
            self.test_results['errors'].append(error_msg)
            return False
    
    def check_database_status(self) -> Dict[str, Any]:
        """Check the current status of the database"""
        logger.info("\n" + "="*50)
        logger.info("CHECKING DATABASE STATUS")
        logger.info("="*50)
        
        try:
            if not self.vector_manager:
                return {"error": "Vector manager not initialized"}
            
            # Get system status
            status = self.vector_manager.get_system_status()
            self.test_results['database_status'] = status
            
            # Print status information
            services = status.get('services', {})
            
            logger.info("📊 DATABASE STATUS:")
            logger.info(f"  - Timestamp: {status.get('timestamp', 'unknown')}")
            
            # Embedding service
            embedding_info = services.get('embedding')
            if embedding_info:
                logger.info(f"  - Embedding Service: ✅ {embedding_info.get('model_name', 'unknown')}")
            else:
                logger.info("  - Embedding Service: ❌ Not available")
            
            # ChromaDB service
            chroma_info = services.get('chroma')
            if chroma_info:
                doc_count = chroma_info.get('document_count', 0)
                collection_name = chroma_info.get('collection_name', 'unknown')
                logger.info(f"  - ChromaDB: ✅ Collection '{collection_name}' with {doc_count} documents")
            else:
                logger.info("  - ChromaDB: ❌ Not available")
            
            # Document service
            doc_info = services.get('document', {})
            total_docs = doc_info.get('total_documents', 0)
            logger.info(f"  - Document Service: ✅ {total_docs} documents stored")
            
            if total_docs > 0:
                metadata_summary = doc_info.get('metadata_summary', {})
                logger.info("  - Document Metadata Summary:")
                for key, values in metadata_summary.items():
                    if isinstance(values, dict):
                        logger.info(f"    - {key}: {dict(list(values.items())[:5])}")  # Show first 5 items
                    else:
                        logger.info(f"    - {key}: {values}")
            
            return status
            
        except Exception as e:
            error_msg = f"Error checking database status: {e}"
            logger.error(error_msg)
            self.test_results['errors'].append(error_msg)
            return {"error": str(e)}
    
    def populate_test_data(self) -> bool:
        """Populate the database with test financial data"""
        logger.info("\n" + "="*50)
        logger.info("POPULATING TEST DATA")
        logger.info("="*50)
        
        try:
            # Financial news test documents
            test_documents = [
                {
                    'text': "Apple Inc. reports record quarterly earnings driven by strong iPhone sales and services revenue. The company exceeded analyst expectations with revenue of $89.5 billion, up 8% year-over-year. CEO Tim Cook highlighted the strength of the services business and growing adoption of Apple's ecosystem.",
                    'metadata': {
                        'category': 'business',
                        'source': 'financial_news',
                        'company': 'Apple',
                        'ticker': 'AAPL',
                        'date': '2024-01-15',
                        'tags': ['earnings', 'tech', 'revenue']
                    }
                },
                {
                    'text': "Federal Reserve signals potential interest rate cuts in 2024 amid cooling inflation data. The central bank's latest meeting minutes suggest policymakers are considering a shift in monetary policy stance as inflation moves closer to the 2% target. Markets rallied on the news with tech stocks leading gains.",
                    'metadata': {
                        'category': 'markets',
                        'source': 'financial_news',
                        'topic': 'monetary_policy',
                        'date': '2024-01-10',
                        'tags': ['fed', 'interest_rates', 'inflation', 'policy']
                    }
                },
                {
                    'text': "Tesla's Q4 delivery numbers disappoint investors as EV competition intensifies. The electric vehicle maker delivered 484,507 vehicles in the fourth quarter, falling short of Wall Street estimates. Increased competition from traditional automakers and new EV startups pressured market share.",
                    'metadata': {
                        'category': 'business',
                        'source': 'financial_news',
                        'company': 'Tesla',
                        'ticker': 'TSLA',
                        'date': '2024-01-08',
                        'tags': ['ev', 'delivery', 'competition', 'automotive']
                    }
                },
                {
                    'text': "Bitcoin reaches new all-time high above $73,000 as institutional adoption accelerates. Major corporations and pension funds continue to allocate portions of their portfolios to cryptocurrency. The approval of spot Bitcoin ETFs has provided easier access for retail investors.",
                    'metadata': {
                        'category': 'crypto',
                        'source': 'financial_news',
                        'asset': 'Bitcoin',
                        'ticker': 'BTC',
                        'date': '2024-01-20',
                        'tags': ['cryptocurrency', 'bitcoin', 'etf', 'institutional']
                    }
                },
                {
                    'text': "Microsoft announces major AI partnership with OpenAI, investing additional $10 billion. The partnership will accelerate development of artificial intelligence technologies and integrate advanced AI capabilities across Microsoft's product suite including Office, Azure, and Bing.",
                    'metadata': {
                        'category': 'tech',
                        'source': 'financial_news',
                        'company': 'Microsoft',
                        'ticker': 'MSFT',
                        'date': '2024-01-12',
                        'tags': ['ai', 'partnership', 'investment', 'technology']
                    }
                },
                {
                    'text': "Oil prices surge 5% on geopolitical tensions and supply concerns. Brent crude reaches $92 per barrel as OPEC+ maintains production cuts and Middle East tensions escalate. Energy sector stocks outperform broader market indices.",
                    'metadata': {
                        'category': 'commodities',
                        'source': 'financial_news',
                        'asset': 'Oil',
                        'date': '2024-01-18',
                        'tags': ['oil', 'commodities', 'geopolitics', 'energy']
                    }
                },
                {
                    'text': "S&P 500 index closes at record high driven by technology and healthcare gains. The benchmark index gained 1.2% to reach 4,850 points, with strong performances from mega-cap technology stocks. Healthcare stocks also contributed to gains on positive clinical trial results.",
                    'metadata': {
                        'category': 'markets',
                        'source': 'financial_news',
                        'index': 'S&P 500',
                        'date': '2024-01-22',
                        'tags': ['index', 'tech', 'healthcare', 'record_high']
                    }
                },
                {
                    'text': "Goldman Sachs revises 2024 GDP growth forecast upward citing resilient consumer spending and labor market strength. The investment bank now expects 2.5% growth compared to previous estimate of 2.1%. Strong employment data and consumer confidence support the revised outlook.",
                    'metadata': {
                        'category': 'economics',
                        'source': 'financial_news',
                        'organization': 'Goldman Sachs',
                        'date': '2024-01-16',
                        'tags': ['gdp', 'forecast', 'consumer', 'labor_market']
                    }
                }
            ]
            
            # Add documents to the system
            logger.info(f"Adding {len(test_documents)} test documents...")
            doc_ids = self.vector_manager.add_documents(
                test_documents,
                generate_embeddings=True,
                add_to_vector_db=True
            )
            
            logger.info(f"✅ Successfully added {len(doc_ids)} documents")
            logger.info(f"Document IDs: {doc_ids[:3]}..." if len(doc_ids) > 3 else f"Document IDs: {doc_ids}")
            
            return True
            
        except Exception as e:
            error_msg = f"Error populating test data: {e}"
            logger.error(error_msg)
            self.test_results['errors'].append(error_msg)
            return False
    
    def test_search_functionality(self) -> Dict[str, Any]:
        """Test different types of search functionality"""
        logger.info("\n" + "="*50)
        logger.info("TESTING SEARCH FUNCTIONALITY")
        logger.info("="*50)
        
        search_results = {}
        
        # Test queries
        test_queries = [
            {
                'name': 'technology_semantic',
                'query': 'artificial intelligence and technology companies',
                'search_type': 'semantic',
                'description': 'Semantic search for AI and tech content'
            },
            {
                'name': 'earnings_text',
                'query': 'earnings revenue quarterly',
                'search_type': 'text',
                'description': 'Text search for earnings-related content'
            },
            {
                'name': 'market_hybrid',
                'query': 'stock market performance gains',
                'search_type': 'hybrid',
                'description': 'Hybrid search combining semantic and text'
            },
            {
                'name': 'crypto_category',
                'query': 'cryptocurrency investment',
                'search_type': 'semantic',
                'description': 'Search specifically in crypto category',
                'metadata_filters': {'category': 'crypto'}
            }
        ]
        
        for test_query in test_queries:
            try:
                logger.info(f"\n🔍 Testing: {test_query['description']}")
                logger.info(f"   Query: '{test_query['query']}'")
                logger.info(f"   Type: {test_query['search_type']}")
                
                # Perform search
                results = self.vector_manager.search(
                    query=test_query['query'],
                    search_type=test_query['search_type'],
                    n_results=3,
                    metadata_filters=test_query.get('metadata_filters')
                )
                
                # Process results
                if results:
                    logger.info(f"   ✅ Found {len(results)} results")
                    
                    # Display top results
                    for i, result in enumerate(results[:2], 1):
                        doc_text = result.get('text', result.get('document', ''))[:100]
                        metadata = result.get('metadata', {})
                        score = result.get('score', result.get('distance', 'N/A'))
                        
                        logger.info(f"   Result {i}:")
                        logger.info(f"     - Text: {doc_text}...")
                        logger.info(f"     - Score: {score}")
                        logger.info(f"     - Category: {metadata.get('category', 'N/A')}")
                        logger.info(f"     - Source: {metadata.get('source', 'N/A')}")
                    
                    search_results[test_query['name']] = {
                        'query': test_query['query'],
                        'search_type': test_query['search_type'],
                        'result_count': len(results),
                        'top_results': results[:3],
                        'status': 'success'
                    }
                else:
                    logger.info("   ❌ No results found")
                    search_results[test_query['name']] = {
                        'query': test_query['query'],
                        'search_type': test_query['search_type'],
                        'result_count': 0,
                        'status': 'no_results'
                    }
                
            except Exception as e:
                error_msg = f"Error in search test '{test_query['name']}': {e}"
                logger.error(error_msg)
                search_results[test_query['name']] = {
                    'query': test_query['query'],
                    'search_type': test_query['search_type'],
                    'status': 'error',
                    'error': str(e)
                }
                self.test_results['errors'].append(error_msg)
        
        self.test_results['search_tests'] = search_results
        return search_results
    
    def test_specialized_searches(self) -> Dict[str, Any]:
        """Test specialized search functions"""
        logger.info("\n" + "="*50)
        logger.info("TESTING SPECIALIZED SEARCHES")
        logger.info("="*50)
        
        specialized_results = {}
        
        # Test category-based search
        try:
            logger.info("\n🏷️ Testing category-based search...")
            category_results = self.vector_manager.search_by_category(
                category='business',
                query='earnings performance',
                n_results=3
            )
            logger.info(f"   Business category search: {len(category_results)} results")
            specialized_results['category_search'] = {
                'category': 'business',
                'result_count': len(category_results),
                'results': category_results[:2]
            }
        except Exception as e:
            logger.error(f"   Error in category search: {e}")
            specialized_results['category_search'] = {'error': str(e)}
        
        # Test source-based search
        try:
            logger.info("\n📰 Testing source-based search...")
            source_results = self.vector_manager.search_by_source(
                source='financial_news',
                query='technology',
                n_results=3
            )
            logger.info(f"   Financial news source search: {len(source_results)} results")
            specialized_results['source_search'] = {
                'source': 'financial_news',
                'result_count': len(source_results),
                'results': source_results[:2]
            }
        except Exception as e:
            logger.error(f"   Error in source search: {e}")
            specialized_results['source_search'] = {'error': str(e)}
        
        return specialized_results
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report"""
        logger.info("\n" + "="*50)
        logger.info("GENERATING TEST REPORT")
        logger.info("="*50)
        
        report_lines = [
            "# FinSightAI Database and Search Test Report",
            f"Generated on: {self.test_results['timestamp']}",
            "",
            "## Database Status"
        ]
        
        # Database status
        db_status = self.test_results.get('database_status', {})
        services = db_status.get('services', {})
        
        if services:
            chroma_info = services.get('chroma', {})
            doc_count = chroma_info.get('document_count', 0)
            
            report_lines.extend([
                f"- Documents in database: {doc_count}",
                f"- Collection name: {chroma_info.get('collection_name', 'N/A')}",
                f"- Embedding model: {services.get('embedding', {}).get('model_name', 'N/A')}",
                ""
            ])
        
        # Search test results
        report_lines.append("## Search Test Results")
        search_tests = self.test_results.get('search_tests', {})
        
        for test_name, result in search_tests.items():
            status = "✅" if result['status'] == 'success' else "❌"
            report_lines.extend([
                f"### {test_name} {status}",
                f"- Query: '{result['query']}'",
                f"- Search Type: {result['search_type']}",
                f"- Results Found: {result.get('result_count', 0)}",
                ""
            ])
        
        # Errors
        if self.test_results.get('errors'):
            report_lines.extend([
                "## Errors Encountered",
                ""
            ])
            for error in self.test_results['errors']:
                report_lines.append(f"- {error}")
        
        report_content = "\n".join(report_lines)
        
        # Save report to file
        report_path = f"database_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"📄 Test report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
        
        return report_content
    
    def run_comprehensive_test(self, populate_data: bool = True) -> bool:
        """Run the complete test suite"""
        logger.info("🚀 Starting comprehensive database and search test...")
        
        try:
            # Step 1: Initialize services
            if not self.initialize_vector_service():
                return False
            
            # Step 2: Check current database status
            self.check_database_status()
            
            # Step 3: Populate test data if requested and database is empty
            current_doc_count = self.test_results.get('database_status', {}).get('services', {}).get('chroma', {}).get('document_count', 0)
            
            if populate_data and current_doc_count == 0:
                logger.info("📝 Database is empty, populating with test data...")
                if not self.populate_test_data():
                    return False
                
                # Re-check status after populating data
                self.check_database_status()
            elif current_doc_count > 0:
                logger.info(f"📊 Database already contains {current_doc_count} documents")
            
            # Step 4: Test search functionality
            self.test_search_functionality()
            
            # Step 5: Test specialized searches
            self.test_specialized_searches()
            
            # Step 6: Generate report
            self.generate_report()
            
            logger.info("\n" + "="*50)
            logger.info("✅ COMPREHENSIVE TEST COMPLETED SUCCESSFULLY")
            logger.info("="*50)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            return False

def main():
    """Main function to run the database test"""
    print("="*60)
    print("   FinSightAI Database and Search Functionality Test")
    print("="*60)
    
    # Create tester instance
    tester = DatabaseTester()
    
    # Run comprehensive test
    success = tester.run_comprehensive_test(populate_data=True)
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("Check the generated report file for detailed results.")
    else:
        print("\n❌ Some tests failed. Check the logs for details.")
    
    return success

if __name__ == "__main__":
    main()
