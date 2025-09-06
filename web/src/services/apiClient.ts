import axios, { AxiosResponse } from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Type definitions
export interface QueryRequest {
  query: string;
  retrieval_method?: 'semantic' | 'text' | 'hybrid';
  insight_type?: 'general' | 'market_analysis' | 'portfolio_advice' | 'news_summary';
  k?: number;
  llm_provider?: 'openai' | 'gemini';
  include_sources?: boolean;
  metadata_filters?: Record<string, any>;
}

export interface InsightResponse {
  insight: string;
  sources?: Array<{
    title: string;
    content: string;
    url?: string;
    published?: string;
    score?: number;
  }>;
  metadata: {
    query: string;
    retrieval_method: string;
    insight_type: string;
    llm_provider: string;
    processing_time: number;
    retrieved_documents: number;
  };
}

export interface NewsArticle {
  id: string;
  title: string;
  content: string;
  url?: string;
  published?: string;
  source: string;
  category?: string;
}

export interface PortfolioData {
  holdings: Array<{
    symbol: string;
    quantity: number;
    current_price: number;
    market_value: number;
    day_change: number;
    day_change_percent: number;
  }>;
  total_value: number;
  total_change: number;
  total_change_percent: number;
  last_updated: string;
}

// API methods
export const apiService = {
  // RAG/Chat endpoints
  async generateInsights(request: QueryRequest): Promise<InsightResponse> {
    const response: AxiosResponse<InsightResponse> = await apiClient.post('/query/insights', request);
    return response.data;
  },

  async askQuestion(query: string): Promise<any> {
    const response = await apiClient.post('/query/ask', { question: query });
    return response.data;
  },

  // News endpoints
  async getLatestNews(limit: number = 20): Promise<NewsArticle[]> {
    const response: AxiosResponse<NewsArticle[]> = await apiClient.get(`/news/latest?limit=${limit}`);
    return response.data;
  },

  async getNewsByCategory(category: string, limit: number = 10): Promise<NewsArticle[]> {
    const response: AxiosResponse<NewsArticle[]> = await apiClient.get(`/news/category/${category}?limit=${limit}`);
    return response.data;
  },

  async searchNews(query: string, limit: number = 10): Promise<NewsArticle[]> {
    const response: AxiosResponse<NewsArticle[]> = await apiClient.get(`/news/search?q=${encodeURIComponent(query)}&limit=${limit}`);
    return response.data;
  },

  // Portfolio endpoints
  async getPortfolio(): Promise<PortfolioData> {
    const response: AxiosResponse<PortfolioData> = await apiClient.get('/portfolio');
    return response.data;
  },

  async getPortfolioInsights(symbol?: string): Promise<any> {
    const url = symbol ? `/portfolio/insights?symbol=${symbol}` : '/portfolio/insights';
    const response = await apiClient.get(url);
    return response.data;
  },

  // System health
  async getSystemStatus(): Promise<any> {
    const response = await apiClient.get('/query/status');
    return response.data;
  },
};

export default apiClient;
