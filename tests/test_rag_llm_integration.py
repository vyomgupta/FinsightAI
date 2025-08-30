"""
End-to-End Tests for RAG + LLM Integration
Tests the complete pipeline from query to embeddings retrieval to LLM output
"""
import os
import sys
import unittest
import logging
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api', 'services'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'vector-service'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockVectorServiceManager:
    """Mock vector service manager for testing"""
    
    def __init__(self):
        self.documents = [
            {
                'id': 'doc1',
                'text': 'Apple Inc. reported strong quarterly earnings with revenue growth of 8% year-over-year. The iPhone segment showed particular strength.',
                'metadata': {'title': 'Apple Q4 Earnings', 'source': 'financial_news', 'category': 'earnings'}
            },
            {
                'id': 'doc2', 
                'text': 'Tesla stock surged 15% after announcing record vehicle deliveries for Q3. The company exceeded analyst expectations.',
                'metadata': {'title': 'Tesla Delivery Record', 'source': 'market_news', 'category': 'automotive'}
            },
            {
                'id': 'doc3',
                'text': 'Federal Reserve indicated potential interest rate cuts in 2024 based on inflation data trends. Markets reacted positively.',
                'metadata': {'title': 'Fed Rate Outlook', 'source': 'economic_news', 'category': 'monetary_policy'}
            }
        ]
    
    def search(self, query, search_type="hybrid", n_results=5, **kwargs):
        """Mock search that returns relevant documents based on keywords"""
        from search_service import SearchResult
        from document_service import Document
        
        results = []
        query_lower = query.lower()
        
        for doc in self.documents:
            # Simple keyword matching for mock
            text_lower = doc['text'].lower()
            score = 0.0
            
            # Calculate mock similarity score
            query_words = query_lower.split()
            for word in query_words:
                if word in text_lower:
                    score += 0.3
            
            if score > 0:
                document = Document(
                    document_id=doc['id'],
                    text=doc['text'],
                    metadata=doc['metadata']
                )
                
                result = SearchResult(
                    document=document,
                    score=min(score, 1.0),
                    search_type=search_type,
                    query=query
                )
                results.append(result)
        
        # Sort by score and limit results
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:n_results]
    
    def get_system_status(self):
        """Mock system status"""
        return {
            'services': {
                'document': {'total_documents': len(self.documents)},
                'chroma': {'document_count': len(self.documents)},
                'embedding': {'model': 'mock-embeddings'}
            }
        }


class MockLLMService:
    """Mock LLM service for testing"""
    
    def __init__(self):
        self.provider = "mock"
        self.model = "mock-gpt"
    
    def generate_insights(self, query, context, provider=None, insight_type="general", **kwargs):
        """Mock insight generation"""
        from llm_service import LLMResponse
        
        # Generate mock response based on context
        if not context.strip():
            content = f"I don't have specific information about '{query}' in my knowledge base."
        else:
            content = f"Based on the available financial data, regarding '{query}': {context[:200]}... [Analysis would continue with AI-generated insights]"
        
        return LLMResponse(
            content=content,
            provider=self.provider,
            model=self.model,
            tokens_used=150,
            response_time=0.5,
            metadata={'mock': True}
        )
    
    def get_service_status(self):
        """Mock service status"""
        return {
            'default_provider': self.provider,
            'available_providers': [self.provider],
            'service_status': 'active'
        }


class TestRAGLLMIntegration(unittest.TestCase):
    """Test cases for RAG + LLM integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock services
        self.mock_vector_manager = MockVectorServiceManager()
        self.mock_llm_service = MockLLMService()
        
        # Import RAG service
        from rag_service import RAGService
        
        # Initialize RAG service with mocks
        self.rag_service = RAGService(
            vector_service_manager=self.mock_vector_manager,
            llm_service=self.mock_llm_service
        )
    
    def test_retrieval_only(self):
        """Test document retrieval without LLM generation"""
        query = "Apple earnings"
        
        retrieval_result = self.rag_service.retrieve_context(
            query=query,
            k=3,
            retrieval_method="hybrid"
        )
        
        # Verify retrieval results
        self.assertIsNotNone(retrieval_result)
        self.assertEqual(retrieval_result.query, query)
        self.assertGreater(retrieval_result.total_retrieved, 0)
        self.assertTrue(len(retrieval_result.search_results) > 0)
        
        # Check context text
        context_text = retrieval_result.get_context_text()
        self.assertIsInstance(context_text, str)
        self.assertGreater(len(context_text), 0)
        
        logger.info(f"Retrieval test passed - found {retrieval_result.total_retrieved} documents")
    
    def test_end_to_end_pipeline(self):
        """Test complete RAG pipeline: query → retrieval → LLM generation"""
        query = "What are the latest trends in Apple stock?"
        
        response = self.rag_service.generate_insights(
            query=query,
            retrieval_method="hybrid",
            insight_type="market_analysis",
            k=3,
            include_sources=True
        )
        
        # Verify response structure
        self.assertIsInstance(response, dict)
        self.assertIn('query', response)
        self.assertIn('insights', response)
        self.assertIn('retrieval', response)
        self.assertIn('generation', response)
        self.assertIn('pipeline', response)
        self.assertIn('sources', response)
        
        # Verify content
        self.assertEqual(response['query'], query)
        self.assertIsInstance(response['insights'], str)
        self.assertGreater(len(response['insights']), 0)
        
        # Verify retrieval info
        self.assertIn('method', response['retrieval'])
        self.assertIn('documents_found', response['retrieval'])
        self.assertGreater(response['retrieval']['documents_found'], 0)
        
        # Verify generation info
        self.assertIn('provider', response['generation'])
        self.assertIn('model', response['generation'])
        self.assertEqual(response['generation']['insight_type'], 'market_analysis')
        
        # Verify pipeline status
        self.assertIn('status', response['pipeline'])
        self.assertIn(response['pipeline']['status'], ['success', 'partial_success'])
        
        # Verify sources
        self.assertIsInstance(response['sources'], list)
        self.assertGreater(len(response['sources']), 0)
        
        logger.info(f"End-to-end test passed - generated {len(response['insights'])} character response")
    
    def test_question_categorization(self):
        """Test automatic question categorization"""
        test_cases = [
            ("What's the latest market trend?", "market_analysis"),
            ("How should I diversify my portfolio?", "portfolio_advice"),
            ("What are the recent news about Tesla?", "news_summary"),
            ("Explain compound interest", "general")
        ]
        
        for question, expected_type in test_cases:
            with self.subTest(question=question):
                response = self.rag_service.ask_question(question, k=2)
                
                self.assertIsInstance(response, dict)
                self.assertIn('generation', response)
                self.assertEqual(response['generation']['insight_type'], expected_type)
                
                logger.info(f"Categorization test passed: '{question}' → {expected_type}")
    
    def test_retrieval_methods(self):
        """Test different retrieval methods"""
        query = "Federal Reserve interest rates"
        methods = ["semantic", "text", "hybrid"]
        
        for method in methods:
            with self.subTest(method=method):
                response = self.rag_service.generate_insights(
                    query=query,
                    retrieval_method=method,
                    k=2
                )
                
                self.assertIsInstance(response, dict)
                self.assertEqual(response['retrieval']['method'], method)
                self.assertGreater(response['retrieval']['documents_found'], 0)
                
                logger.info(f"Retrieval method test passed: {method}")
    
    def test_insight_types(self):
        """Test different insight types"""
        query = "Tesla stock performance"
        insight_types = ["general", "market_analysis", "portfolio_advice", "news_summary"]
        
        for insight_type in insight_types:
            with self.subTest(insight_type=insight_type):
                response = self.rag_service.generate_insights(
                    query=query,
                    insight_type=insight_type,
                    k=2
                )
                
                self.assertIsInstance(response, dict)
                self.assertEqual(response['generation']['insight_type'], insight_type)
                self.assertIsInstance(response['insights'], str)
                
                logger.info(f"Insight type test passed: {insight_type}")
    
    def test_service_status(self):
        """Test service status reporting"""
        status = self.rag_service.get_service_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('rag_service', status)
        self.assertIn('vector_services', status)
        self.assertIn('llm_service', status)
        self.assertIn('pipeline_capabilities', status)
        
        # Check RAG service status
        self.assertEqual(status['rag_service']['status'], 'active')
        self.assertEqual(status['rag_service']['components']['retriever'], 'active')
        self.assertEqual(status['rag_service']['components']['llm_generator'], 'active')
        
        # Check capabilities
        capabilities = status['pipeline_capabilities']
        self.assertTrue(capabilities['end_to_end_generation'])
        self.assertIn('general', capabilities['supported_insight_types'])
        self.assertIn('hybrid', capabilities['supported_retrieval_methods'])
        
        logger.info("Service status test passed")
    
    def test_error_handling(self):
        """Test error handling in the pipeline"""
        # Test with mock that raises exception
        with patch.object(self.mock_vector_manager, 'search', side_effect=Exception("Mock search error")):
            response = self.rag_service.generate_insights(
                query="test query",
                k=2
            )
            
            self.assertIsInstance(response, dict)
            self.assertIn('error', response)
            self.assertEqual(response['pipeline']['status'], 'error')
            
            logger.info("Error handling test passed")
    
    def test_performance_metrics(self):
        """Test performance metrics collection"""
        query = "Apple vs Tesla stock comparison"
        
        response = self.rag_service.generate_insights(
            query=query,
            k=3
        )
        
        # Check timing information
        self.assertIn('pipeline', response)
        self.assertIn('total_time', response['pipeline'])
        self.assertIsInstance(response['pipeline']['total_time'], float)
        self.assertGreater(response['pipeline']['total_time'], 0)
        
        # Check LLM metrics
        if 'tokens_used' in response['generation']:
            self.assertIsInstance(response['generation']['tokens_used'], int)
            self.assertGreater(response['generation']['tokens_used'], 0)
        
        if 'response_time' in response['generation']:
            self.assertIsInstance(response['generation']['response_time'], float)
            self.assertGreater(response['generation']['response_time'], 0)
        
        logger.info(f"Performance test passed - pipeline time: {response['pipeline']['total_time']:.3f}s")


class TestWithoutLLMService(unittest.TestCase):
    """Test RAG service behavior when LLM service is not available"""
    
    def setUp(self):
        """Set up test fixtures without LLM service"""
        from rag_service import RAGService
        
        self.mock_vector_manager = MockVectorServiceManager()
        self.rag_service = RAGService(
            vector_service_manager=self.mock_vector_manager,
            llm_service=None  # No LLM service
        )
    
    def test_retrieval_without_llm(self):
        """Test retrieval-only functionality when LLM is not available"""
        query = "Apple earnings report"
        
        response = self.rag_service.generate_insights(
            query=query,
            k=2
        )
        
        self.assertIsInstance(response, dict)
        self.assertEqual(response['query'], query)
        self.assertIn("LLM service not available", response['insights'])
        self.assertEqual(response['pipeline']['status'], 'partial_success')
        
        # Should still have retrieval results
        self.assertGreater(response['retrieval']['documents_found'], 0)
        
        logger.info("Retrieval without LLM test passed")


def create_mock_data_pipeline():
    """Create a more comprehensive mock data pipeline"""
    mock_documents = [
        {
            'id': 'news1',
            'text': 'Microsoft reported quarterly revenue of $65.6 billion, up 12% year-over-year, driven by strong cloud and productivity segment growth.',
            'metadata': {'title': 'Microsoft Q3 Results', 'source': 'tech_news', 'category': 'earnings', 'date': '2024-01-15'}
        },
        {
            'id': 'analysis1',
            'text': 'Technical analysis shows Apple stock forming a bullish pattern with strong support at $180. RSI indicates potential upside momentum.',
            'metadata': {'title': 'Apple Technical Analysis', 'source': 'market_analysis', 'category': 'technical', 'date': '2024-01-14'}
        },
        {
            'id': 'portfolio1',
            'text': 'Diversified portfolio allocation should include 60% stocks, 30% bonds, and 10% alternatives for moderate risk tolerance investors.',
            'metadata': {'title': 'Portfolio Allocation Guide', 'source': 'investment_advice', 'category': 'portfolio', 'date': '2024-01-10'}
        }
    ]
    
    return mock_documents


class TestIntegrationWithMockData(unittest.TestCase):
    """Integration tests with more comprehensive mock data"""
    
    def setUp(self):
        """Set up with comprehensive mock data"""
        from rag_service import RAGService
        
        # Create enhanced mock with more data
        self.mock_vector_manager = MockVectorServiceManager()
        self.mock_vector_manager.documents.extend(create_mock_data_pipeline())
        
        self.mock_llm_service = MockLLMService()
        self.rag_service = RAGService(
            vector_service_manager=self.mock_vector_manager,
            llm_service=self.mock_llm_service
        )
    
    def test_comprehensive_pipeline(self):
        """Test the pipeline with comprehensive mock data"""
        test_queries = [
            ("What are Microsoft's latest earnings?", "market_analysis"),
            ("How should I allocate my investment portfolio?", "portfolio_advice"),
            ("Give me technical analysis on Apple stock", "market_analysis"),
            ("What's the latest financial news?", "news_summary")
        ]
        
        for query, expected_type in test_queries:
            with self.subTest(query=query):
                response = self.rag_service.ask_question(query, k=3)
                
                self.assertIsInstance(response, dict)
                self.assertIn('insights', response)
                self.assertGreater(len(response['insights']), 0)
                self.assertEqual(response['generation']['insight_type'], expected_type)
                
                # Should find relevant documents
                self.assertGreater(response['retrieval']['documents_found'], 0)
                
                logger.info(f"Comprehensive test passed: '{query}' → {response['retrieval']['documents_found']} docs")


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestRAGLLMIntegration))
    suite.addTest(unittest.makeSuite(TestWithoutLLMService))
    suite.addTest(unittest.makeSuite(TestIntegrationWithMockData))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print("\n✅ All RAG + LLM integration tests passed!")
        print(f"Ran {result.testsRun} tests successfully")
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        for test, error in result.failures + result.errors:
            print(f"Failed: {test} - {error}")
