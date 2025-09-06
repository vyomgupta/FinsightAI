"""
LLM Service for FinSightAI
Integrates with various Large Language Models (OpenAI GPT, Google Gemini) for generating insights
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
from dataclasses import dataclass
from enum import Enum

# Import for API calls
import requests
from time import sleep

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"


@dataclass
class LLMResponse:
    """
    Represents a response from an LLM
    """
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    generated_at: str = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'content': self.content,
            'provider': self.provider,
            'model': self.model,
            'tokens_used': self.tokens_used,
            'response_time': self.response_time,
            'metadata': self.metadata,
            'generated_at': self.generated_at
        }


class BaseLLMClient:
    """
    Base class for LLM clients
    """
    
    def __init__(self, api_key: str, model: str):
        """
        Initialize base LLM client
        
        Args:
            api_key: API key for the service
            model: Model name to use
        """
        self.api_key = api_key
        self.model = model
        self.provider = "base"
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Generate response from LLM
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
        
        Returns:
            LLMResponse object
        """
        raise NotImplementedError("Subclasses must implement generate method")


class OpenAIClient(BaseLLMClient):
    """
    OpenAI GPT client
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key
            model: Model to use (e.g., gpt-3.5-turbo, gpt-4)
        """
        super().__init__(api_key, model)
        self.provider = "openai"
        self.base_url = "https://api.openai.com/v1"
    
    def generate(self, prompt: str, 
                 system_prompt: Optional[str] = None,
                 max_tokens: int = 1000,
                 temperature: float = 0.7,
                 **kwargs) -> LLMResponse:
        """
        Generate response using OpenAI API
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            **kwargs: Additional parameters
        
        Returns:
            LLMResponse object
        """
        try:
            import time
            start_time = time.time()
            
            # Prepare headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Prepare request data
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                **kwargs
            }
            
            # Make API call
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Extract response content
            content = result['choices'][0]['message']['content']
            tokens_used = result.get('usage', {}).get('total_tokens')
            
            return LLMResponse(
                content=content,
                provider=self.provider,
                model=self.model,
                tokens_used=tokens_used,
                response_time=response_time,
                metadata=result.get('usage', {})
            )
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return LLMResponse(
                content=f"Error generating response: {str(e)}",
                provider=self.provider,
                model=self.model,
                metadata={"error": str(e)}
            )


class GeminiClient(BaseLLMClient):
    """
    Google Gemini client using the official google-generativeai library
    """
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google API key
            model: Model to use (e.g., gemini-2.5-flash, gemini-pro)
        """
        super().__init__(api_key, model)
        self.provider = "gemini"
        
        # Initialize Google Generative AI client
        try:
            import os
            os.environ['GEMINI_API_KEY'] = api_key
            
            from google import genai
            from google.genai import types
            
            self.client = genai.Client()
            self.types = types
            logger.info(f"Gemini client initialized with model: {model}")
        except ImportError as e:
            logger.error(f"Failed to import google.genai: {e}")
            logger.info("Please install: pip install google-genai")
            self.client = None
            self.types = None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.client = None
            self.types = None
    
    def generate(self, prompt: str,
                 system_prompt: Optional[str] = None,
                 max_tokens: int = 1000,
                 temperature: float = 0.7,
                 **kwargs) -> LLMResponse:
        """
        Generate response using Gemini API
        
        Args:
            prompt: Input prompt
            system_prompt: Optional system prompt (will be prepended to prompt)
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            **kwargs: Additional parameters
        
        Returns:
            LLMResponse object
        """
        try:
            if not self.client:
                return LLMResponse(
                    content="Gemini client not available. Please install google-generativeai package.",
                    provider=self.provider,
                    model=self.model,
                    metadata={"error": "Client not initialized"}
                )
            
            import time
            start_time = time.time()
            
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Generate response using the official client with optimized config
            if self.types:
                # Use thinking config for faster responses and lower costs
                config = self.types.GenerateContentConfig(
                    thinking_config=self.types.ThinkingConfig(thinking_budget=0)  # Disables thinking
                )
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                    config=config
                )
            else:
                # Fallback without config if types not available
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=full_prompt
                )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Extract response content
            content = response.text if hasattr(response, 'text') else str(response)
            
            return LLMResponse(
                content=content,
                provider=self.provider,
                model=self.model,
                response_time=response_time,
                metadata={"google_genai": True}
            )
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return LLMResponse(
                content=f"Error generating response: {str(e)}",
                provider=self.provider,
                model=self.model,
                metadata={"error": str(e)}
            )


class LLMService:
    """
    Main LLM service that manages multiple providers
    """
    
    def __init__(self, 
                 default_provider: str = "openai",
                 api_keys: Optional[Dict[str, str]] = None,
                 models: Optional[Dict[str, str]] = None,
                 generation_params: Optional[Dict[str, Any]] = None):
        """
        Initialize LLM service
        
        Args:
            default_provider: Default LLM provider to use
            api_keys: Dictionary of API keys for each provider
            models: Dictionary of models for each provider
            generation_params: Dictionary of default generation parameters
        """
        self.default_provider = default_provider
        self.api_keys = api_keys or {}
        self.models = models or {
            "openai": "gpt-3.5-turbo",
            "gemini": "gemini-2.5-flash",
            "anthropic": "claude-3-haiku-20240307"
        }
        self.generation_params = generation_params or {
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        # Initialize clients
        self.clients = {}
        self._initialize_clients()
        
        logger.info(f"LLM Service initialized with default provider: {default_provider}")
    
    def _initialize_clients(self) -> None:
        """Initialize LLM clients based on available API keys"""
        try:
            # Initialize OpenAI client
            if "openai" in self.api_keys and self.api_keys["openai"]:
                self.clients["openai"] = OpenAIClient(
                    api_key=self.api_keys["openai"],
                    model=self.models.get("openai", "gpt-3.5-turbo")
                )
                logger.info("OpenAI client initialized")
            
            # Initialize Gemini client
            if "gemini" in self.api_keys and self.api_keys["gemini"]:
                self.clients["gemini"] = GeminiClient(
                    api_key=self.api_keys["gemini"],
                    model=self.models.get("gemini", "gemini-2.5-flash")
                )
                logger.info("Gemini client initialized")
            
            # TODO: Add Anthropic client initialization here when implemented
            # if "anthropic" in self.api_keys and self.api_keys["anthropic"]:
            #     self.clients["anthropic"] = AnthropicClient(
            #         api_key=self.api_keys["anthropic"],
            #         model=self.models.get("anthropic", "claude-3-haiku-20240307")
            #     )
            #     logger.info("Anthropic client initialized")
            
            if not self.clients:
                logger.warning("No LLM clients initialized - no API keys provided or invalid keys")
                
        except Exception as e:
            logger.error(f"Error initializing LLM clients: {e}")
    
    def generate_insights(self,
                         query: str,
                         context: str,
                         provider: Optional[str] = None,
                         insight_type: str = "general",
                         **kwargs) -> LLMResponse:
        """
        Generate insights based on query and retrieved context
        
        Args:
            query: User query
            context: Retrieved context from vector database
            provider: LLM provider to use
            insight_type: Type of insight to generate
            **kwargs: Additional generation parameters
        
        Returns:
            LLMResponse with generated insights
        """
        try:
            provider = provider or self.default_provider
            
            if provider not in self.clients:
                return LLMResponse(
                    content=f"Provider {provider} not available or not configured. Available: {self.get_available_providers()}",
                    provider=provider,
                    model="unknown",
                    metadata={"error": f"Provider {provider} not configured"}
                )
            
            client = self.clients[provider]
            
            # Prepare system prompt based on insight type
            system_prompt = self._get_system_prompt(insight_type)
            
            # Prepare user prompt
            user_prompt = self._prepare_prompt(query, context, insight_type)
            
            # Combine default generation parameters with kwargs
            gen_params = {**self.generation_params, **kwargs}
            
            # Generate response
            response = client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                **gen_params
            )
            
            logger.info(f"Generated insights using {provider} for query: '{query[:50]}...'")
            return response
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return LLMResponse(
                content=f"Error generating insights: {str(e)}",
                provider=provider or "unknown",
                model="unknown",
                metadata={"error": str(e)}
            )
    
    def _get_system_prompt(self, insight_type: str) -> str:
        """Get system prompt based on insight type"""
        system_prompts = {
            "general": """You are a financial AI assistant that provides intelligent insights based on retrieved financial documents. 
            Analyze the provided context and answer questions accurately and helpfully. 
            Focus on actionable insights and be concise but informative.""",
            
            "market_analysis": """You are a market analyst AI that specializes in financial market analysis. 
            Provide detailed market insights, trends, and analysis based on the retrieved financial data. 
            Include relevant metrics, comparisons, and forward-looking perspectives.""",
            
            "portfolio_advice": """You are a portfolio management AI assistant. 
            Provide investment advice and portfolio insights based on the retrieved financial information. 
            Consider risk factors, diversification, and long-term investment strategies.""",
            
            "news_summary": """You are a financial news analyst AI. 
            Summarize and analyze the provided financial news and information. 
            Highlight key developments, their implications, and potential market impacts."""
        }
        
        return system_prompts.get(insight_type, system_prompts["general"])
    
    def _prepare_prompt(self, query: str, context: str, insight_type: str) -> str:
        """Prepare the user prompt with query and context"""
        if not context.strip():
            return f"""
Query: {query}

I don't have specific relevant documents in my knowledge base to answer this query. 
Please provide a general response based on your training knowledge, but indicate that 
you don't have access to current specific data on this topic.
"""
        
        return f"""
Based on the following financial documents and information, please answer the user's query:

QUERY: {query}

RELEVANT DOCUMENTS:
{context}

Please provide a comprehensive and insightful response based on the above information. 
If the documents don't fully address the query, please indicate what information is missing 
and provide the best response possible with the available data.
"""
    
    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers"""
        return list(self.clients.keys())
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get LLM service status"""
        return {
            'default_provider': self.default_provider,
            'available_providers': self.get_available_providers(),
            'configured_models': self.models,
            'service_status': 'active' if self.clients else 'no_providers_configured'
        }


# Factory functions
def create_llm_service(config: Optional[Dict[str, Any]] = None) -> LLMService:
    """
    Factory function to create an LLM service
    
    Args:
        config: Configuration dictionary with API keys and settings
    
    Returns:
        Configured LLMService instance
    """
    from api.utils.config import get_llm_config
    
    if config is None:
        config = get_llm_config() # Load from global config manager
    
    # Load API keys from environment variables if not provided
    api_keys = config.get('api_keys', {})
    if 'openai' not in api_keys and os.getenv('OPENAI_API_KEY'):
        api_keys['openai'] = os.getenv('OPENAI_API_KEY')
    if 'gemini' not in api_keys and os.getenv('GEMINI_API_KEY'):
        api_keys['gemini'] = os.getenv('GEMINI_API_KEY')
    if 'anthropic' not in api_keys and os.getenv('ANTHROPIC_API_KEY'):
        api_keys['anthropic'] = os.getenv('ANTHROPIC_API_KEY')
    
    # Load models from environment variables if not provided
    models = config.get('models', {})
    if 'openai' not in models and os.getenv('OPENAI_MODEL'):
        models['openai'] = os.getenv('OPENAI_MODEL')
    if 'gemini' not in models and os.getenv('GEMINI_MODEL'):
        models['gemini'] = os.getenv('GEMINI_MODEL')
    if 'anthropic' not in models and os.getenv('ANTHROPIC_MODEL'):
        models['anthropic'] = os.getenv('ANTHROPIC_MODEL')
    
    return LLMService(
        default_provider=config.get('default_provider', 'gemini'),
        api_keys=api_keys,
        models=models,
        generation_params=config.get('generation_params', {})
    )


def get_default_llm_service() -> LLMService:
    """Get a default LLM service with environment-based configuration"""
    return create_llm_service()
