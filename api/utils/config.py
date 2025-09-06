"""
Configuration Management for FinSightAI
Handles API keys, service settings, and environment configuration
"""
import os
import logging
from typing import Dict, Any, Optional
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Centralized configuration manager for FinSightAI
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file or os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
        self.config = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file and environment variables"""
        try:
            # Load .env file if it exists
            try:
                from dotenv import load_dotenv
                load_dotenv()
                logger.info("Environment variables loaded from .env file")
            except ImportError:
                logger.info("python-dotenv not available, skipping .env file loading")
            except Exception as e:
                logger.warning(f"Could not load .env file: {e}")
            
            # Load from file if it exists
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self.config = {}
                logger.info("No configuration file found, using defaults")
            
            # Override with environment variables
            self._load_from_environment()
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config = {}
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables"""
        try:
            # LLM API Keys
            if os.getenv('OPENAI_API_KEY'):
                self.set_nested('llm.api_keys.openai', os.getenv('OPENAI_API_KEY'))
            
            if os.getenv('GEMINI_API_KEY'):
                self.set_nested('llm.api_keys.gemini', os.getenv('GEMINI_API_KEY'))
            
            if os.getenv('ANTHROPIC_API_KEY'):
                self.set_nested('llm.api_keys.anthropic', os.getenv('ANTHROPIC_API_KEY'))
            
            # LLM Models
            if os.getenv('OPENAI_MODEL'):
                self.set_nested('llm.models.openai', os.getenv('OPENAI_MODEL'))
            if os.getenv('GEMINI_MODEL'):
                self.set_nested('llm.models.gemini', os.getenv('GEMINI_MODEL'))
            if os.getenv('ANTHROPIC_MODEL'):
                self.set_nested('llm.models.anthropic', os.getenv('ANTHROPIC_MODEL'))
            
            # Default LLM provider
            if os.getenv('DEFAULT_LLM_PROVIDER'):
                self.set_nested('llm.default_provider', os.getenv('DEFAULT_LLM_PROVIDER'))
            
            # Vector service configuration
            if os.getenv('CHROMA_PERSIST_DIR'):
                self.set_nested('vector_services.chroma.persist_directory', os.getenv('CHROMA_PERSIST_DIR'))
            
            if os.getenv('EMBEDDING_MODEL'):
                self.set_nested('vector_services.embedding.model_name', os.getenv('EMBEDDING_MODEL'))
            
            # Jina API key for embeddings
            jina_api_key = os.getenv('JINA_API_KEY')
            if jina_api_key:
                self.set_nested('vector_services.embedding.jina_api_key', jina_api_key)
                logger.info(f"JINA_API_KEY loaded from environment: {jina_api_key}")
            else:
                logger.warning("JINA_API_KEY not found in environment variables")
            
            # API configuration
            if os.getenv('API_HOST'):
                self.set_nested('api.host', os.getenv('API_HOST'))
            
            if os.getenv('API_PORT'):
                self.set_nested('api.port', int(os.getenv('API_PORT')))
            
            # Portfolio API Configuration
            if os.getenv('PORTFOLIO_API_URL'):
                self.set_nested('portfolio_api.url', os.getenv('PORTFOLIO_API_URL'))
            if os.getenv('PORTFOLIO_API_KEY'):
                self.set_nested('portfolio_api.api_key', os.getenv('PORTFOLIO_API_KEY'))
            
        except Exception as e:
            logger.error(f"Error loading environment variables: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (supports dot notation like 'llm.api_keys.openai')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            logger.error(f"Error getting config key '{key}': {e}")
            return default
    
    def set_nested(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        try:
            keys = key.split('.')
            current = self.config
            
            # Navigate to parent
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            # Set the value
            current[keys[-1]] = value
            
        except Exception as e:
            logger.error(f"Error setting config key '{key}': {e}")
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM service configuration"""
        return {
            'default_provider': self.get('llm.default_provider', 'gemini'),
            'api_keys': self.get('llm.api_keys', {}),
            'models': self.get('llm.models', {
                'openai': 'gpt-3.5-turbo',
                'gemini': 'gemini-2.5-flash'
            }),
            'generation_params': self.get('llm.generation_params', {
                'max_tokens': 1000,
                'temperature': 0.7
            })
        }
    
    def get_vector_service_config(self) -> Dict[str, Any]:
        """Get vector service configuration"""
        return {
            'embedding': {
                'model_name': self.get('vector_services.embedding.model_name', 'jina-embeddings-v3'),
                'model_type': self.get('vector_services.embedding.model_type', 'jina'),
                'jina_api_key': self.get('vector_services.embedding.jina_api_key'),
                'cache_dir': self.get('vector_services.embedding.cache_dir', './vector_services/embeddings')
            },
            'chroma': {
                'persist_directory': self.get('vector_services.chroma.persist_directory', './vector_services/chroma_db'),
                'collection_name': self.get('vector_services.chroma.collection_name', 'finsight_documents')
            },
            'document': {
                'storage_dir': self.get('vector_services.document.storage_dir', './vector_services/documents')
            },
            'search': {
                'default_search_type': self.get('vector_services.search.default_search_type', 'hybrid'),
                'semantic_weight': self.get('vector_services.search.semantic_weight', 0.7),
                'text_weight': self.get('vector_services.search.text_weight', 0.3)
            }
        }
    
    def get_rag_config(self) -> Dict[str, Any]:
        """Get RAG service configuration"""
        return {
            'retriever': {
                'default_k': self.get('rag.retriever.default_k', 5),
                'default_similarity_threshold': self.get('rag.retriever.default_similarity_threshold', 0.5),
                'max_context_length': self.get('rag.retriever.max_context_length', 4000)
            },
            'generation': {
                'insight_types': self.get('rag.generation.insight_types', [
                    'general', 'market_analysis', 'portfolio_advice', 'news_summary'
                ]),
                'default_insight_type': self.get('rag.generation.default_insight_type', 'general')
            }
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API service configuration"""
        return {
            'host': self.get('api.host', '0.0.0.0'),
            'port': self.get('api.port', 8000),
            'debug': self.get('api.debug', False),
            'cors_origins': self.get('api.cors_origins', ['*']),
            'rate_limiting': self.get('api.rate_limiting', {
                'enabled': True,
                'requests_per_minute': 60
            })
        }
    
    def get_data_ingestion_config(self) -> Dict[str, Any]:
        """Get data ingestion configuration"""
        return {
            'rss_feeds': self.get('data_ingestion.rss_feeds', []),
            'update_frequency': self.get('data_ingestion.update_frequency', 3600),  # seconds
            'data_directories': {
                'raw': self.get('data_ingestion.directories.raw', './data/raw'),
                'processed': self.get('data_ingestion.directories.processed', './data/processed')
            },
            'batch_size': self.get('data_ingestion.batch_size', 100)
        }
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            # Ensure directory exists
            config_dir = os.path.dirname(self.config_file)
            os.makedirs(config_dir, exist_ok=True)
            
            # Save configuration (excluding sensitive data)
            safe_config = self._get_safe_config()
            
            with open(self.config_file, 'w') as f:
                json.dump(safe_config, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def _get_safe_config(self) -> Dict[str, Any]:
        """Get configuration without sensitive data for saving"""
        safe_config = {}
        
        for key, value in self.config.items():
            if key == 'llm' and isinstance(value, dict):
                # Don't save API keys
                safe_llm = value.copy()
                if 'api_keys' in safe_llm:
                    safe_llm['api_keys'] = {
                        provider: '***CONFIGURED***' if api_key else None
                        for provider, api_key in safe_llm['api_keys'].items()
                    }
                safe_config[key] = safe_llm
            else:
                safe_config[key] = value
        
        return safe_config
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        validation_result = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        try:
            # Check LLM configuration
            llm_config = self.get_llm_config()
            if not llm_config['api_keys']:
                validation_result['warnings'].append("No LLM API keys configured")
            
            # Check vector service configuration
            vector_config = self.get_vector_service_config()
            
            # Check if directories exist or can be created
            for service, config in vector_config.items():
                if isinstance(config, dict):
                    for key, path in config.items():
                        if 'dir' in key and isinstance(path, str):
                            try:
                                os.makedirs(path, exist_ok=True)
                            except Exception as e:
                                validation_result['errors'].append(f"Cannot create directory {path}: {e}")
                                validation_result['valid'] = False
            
            return validation_result
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Configuration validation error: {e}")
            return validation_result
    
    def get_full_config(self) -> Dict[str, Any]:
        """Get complete configuration"""
        return {
            'llm': self.get_llm_config(),
            'vector_services': self.get_vector_service_config(),
            'rag': self.get_rag_config(),
            'api': self.get_api_config(),
            'data_ingestion': self.get_data_ingestion_config()
        }


# Global configuration instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_llm_config() -> Dict[str, Any]:
    """Get LLM configuration"""
    return get_config_manager().get_llm_config()


def get_vector_service_config() -> Dict[str, Any]:
    """Get vector service configuration"""
    return get_config_manager().get_vector_service_config()


def get_rag_config() -> Dict[str, Any]:
    """Get RAG configuration"""
    return get_config_manager().get_rag_config()


def get_api_config() -> Dict[str, Any]:
    """Get API configuration"""
    return get_config_manager().get_api_config()

def get_portfolio_api_config() -> Dict[str, Any]:
    """Get Portfolio API configuration"""
    config_manager = get_config_manager()
    return {
        'url': os.getenv('PORTFOLIO_API_URL'),
        'api_key': os.getenv('PORTFOLIO_API_KEY')
    }


if __name__ == "__main__":
    # Test configuration manager
    try:
        config_manager = get_config_manager()
        
        # Print all configurations
        full_config = config_manager.get_full_config()
        print(json.dumps(full_config, indent=2))
        
        # Validate configuration
        validation = config_manager.validate_config()
        print(f"Configuration validation: {validation}")
        
    except Exception as e:
        print(f"Error testing configuration manager: {e}")
