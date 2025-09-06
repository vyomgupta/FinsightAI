import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Avatar,
  Chip,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Send,
  SmartToy,
  Person,
  TrendingUp,
  ExpandMore,
  Settings,
  Source,
} from '@mui/icons-material';
import { apiService, QueryRequest, InsightResponse } from '../services/apiClient';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  metadata?: any;
  sources?: any[];
}

const ChatBot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  
  // RAG Settings
  const [retrievalMethod, setRetrievalMethod] = useState<'semantic' | 'text' | 'hybrid'>('hybrid');
  const [insightType, setInsightType] = useState<'general' | 'market_analysis' | 'portfolio_advice' | 'news_summary'>('general');
  const [llmProvider, setLlmProvider] = useState<'openai' | 'gemini'>('gemini');

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add welcome message
  useEffect(() => {
    const welcomeMessage: Message = {
      id: 'welcome',
      content: `Hello! I'm your FinSightAI assistant. I can help you with:

• Market analysis and financial insights
• Portfolio recommendations and advice  
• Latest financial news summaries
• General financial questions

What would you like to explore today?`,
      isUser: false,
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const request: QueryRequest = {
        query: inputValue,
        retrieval_method: retrievalMethod,
        insight_type: insightType,
        llm_provider: llmProvider,
        include_sources: true,
        k: 5,
      };

      const response: InsightResponse = await apiService.generateInsights(request);

      const botMessage: Message = {
        id: Date.now().toString() + '_bot',
        content: response.insight,
        isUser: false,
        timestamp: new Date(),
        metadata: response.metadata,
        sources: response.sources,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to get response');
      
      const errorMessage: Message = {
        id: Date.now().toString() + '_error',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getSampleQuestions = () => [
    "What's the current market sentiment?",
    "Analyze my portfolio performance",
    "What are the latest tech stock trends?",
    "Should I invest in renewable energy stocks?",
    "Summarize today's financial news",
  ];

  return (
    <Grid container spacing={3}>
      {/* Chat Area */}
      <Grid item xs={12} md={8}>
        <Paper elevation={2} sx={{ height: '70vh', display: 'flex', flexDirection: 'column' }}>
          {/* Header */}
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', bgcolor: 'primary.main', color: 'white' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <SmartToy sx={{ mr: 1 }} />
                <Typography variant="h6">AI Financial Assistant</Typography>
              </Box>
              <Button
                size="small"
                startIcon={<Settings />}
                onClick={() => setShowSettings(!showSettings)}
                sx={{ color: 'white' }}
              >
                Settings
              </Button>
            </Box>
          </Box>

          {/* Settings Panel */}
          {showSettings && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography>RAG Configuration</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Retrieval Method</InputLabel>
                      <Select
                        value={retrievalMethod}
                        label="Retrieval Method"
                        onChange={(e) => setRetrievalMethod(e.target.value as any)}
                      >
                        <MenuItem value="semantic">Semantic Search</MenuItem>
                        <MenuItem value="text">Text Search</MenuItem>
                        <MenuItem value="hybrid">Hybrid Search</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Insight Type</InputLabel>
                      <Select
                        value={insightType}
                        label="Insight Type"
                        onChange={(e) => setInsightType(e.target.value as any)}
                      >
                        <MenuItem value="general">General</MenuItem>
                        <MenuItem value="market_analysis">Market Analysis</MenuItem>
                        <MenuItem value="portfolio_advice">Portfolio Advice</MenuItem>
                        <MenuItem value="news_summary">News Summary</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small">
                      <InputLabel>LLM Provider</InputLabel>
                      <Select
                        value={llmProvider}
                        label="LLM Provider"
                        onChange={(e) => setLlmProvider(e.target.value as any)}
                      >
                        <MenuItem value="openai">OpenAI GPT</MenuItem>
                        <MenuItem value="gemini">Google Gemini</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Messages */}
          <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
            {messages.map((message) => (
              <Box key={message.id} sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
                  <Avatar sx={{ bgcolor: message.isUser ? 'primary.main' : 'secondary.main', mr: 1 }}>
                    {message.isUser ? <Person /> : <SmartToy />}
                  </Avatar>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      {message.isUser ? 'You' : 'FinSightAI'} • {formatTimestamp(message.timestamp)}
                    </Typography>
                    <Paper
                      sx={{
                        p: 2,
                        mt: 1,
                        bgcolor: message.isUser ? 'primary.light' : 'grey.100',
                        color: message.isUser ? 'white' : 'text.primary',
                      }}
                    >
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {message.content}
                      </Typography>
                      
                      {/* Metadata */}
                      {message.metadata && (
                        <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                          <Typography variant="caption" color="text.secondary">
                            Processing time: {message.metadata.processing_time?.toFixed(2)}s • 
                            Documents: {message.metadata.retrieved_documents} • 
                            Method: {message.metadata.retrieval_method}
                          </Typography>
                        </Box>
                      )}
                      
                      {/* Sources */}
                      {message.sources && message.sources.length > 0 && (
                        <Accordion sx={{ mt: 2 }}>
                          <AccordionSummary expandIcon={<ExpandMore />}>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Source sx={{ mr: 1 }} />
                              <Typography variant="subtitle2">
                                Sources ({message.sources.length})
                              </Typography>
                            </Box>
                          </AccordionSummary>
                          <AccordionDetails>
                            {message.sources.map((source, index) => (
                              <Card key={index} sx={{ mb: 1 }}>
                                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                  <Typography variant="subtitle2" gutterBottom>
                                    {source.title}
                                  </Typography>
                                  <Typography variant="body2" color="text.secondary">
                                    {source.content?.substring(0, 200)}...
                                  </Typography>
                                  {source.score && (
                                    <Chip
                                      label={`Relevance: ${(source.score * 100).toFixed(1)}%`}
                                      size="small"
                                      sx={{ mt: 1 }}
                                    />
                                  )}
                                </CardContent>
                              </Card>
                            ))}
                          </AccordionDetails>
                        </Accordion>
                      )}
                    </Paper>
                  </Box>
                </Box>
              </Box>
            ))}
            
            {isLoading && (
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'secondary.main', mr: 1 }}>
                  <SmartToy />
                </Avatar>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CircularProgress size={20} sx={{ mr: 2 }} />
                  <Typography variant="body2" color="text.secondary">
                    FinSightAI is thinking...
                  </Typography>
                </Box>
              </Box>
            )}
            
            <div ref={messagesEndRef} />
          </Box>

          {/* Error Alert */}
          {error && (
            <Alert severity="error" onClose={() => setError(null)} sx={{ m: 2 }}>
              {error}
            </Alert>
          )}

          {/* Input Area */}
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                multiline
                maxRows={3}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about markets, news, or your portfolio..."
                disabled={isLoading}
                variant="outlined"
              />
              <Button
                variant="contained"
                onClick={handleSendMessage}
                disabled={isLoading || !inputValue.trim()}
                sx={{ minWidth: 60 }}
              >
                <Send />
              </Button>
            </Box>
          </Box>
        </Paper>
      </Grid>

      {/* Sample Questions Sidebar */}
      <Grid item xs={12} md={4}>
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <TrendingUp sx={{ mr: 1 }} />
            Sample Questions
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Try these questions to explore FinSightAI's capabilities:
          </Typography>
          {getSampleQuestions().map((question, index) => (
            <Chip
              key={index}
              label={question}
              variant="outlined"
              onClick={() => setInputValue(question)}
              sx={{ m: 0.5, cursor: 'pointer' }}
              size="small"
            />
          ))}
        </Paper>

        {/* System Status */}
        <Paper elevation={2} sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            System Status
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'success.main', mr: 1 }} />
            <Typography variant="body2">Vector Database: Online</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'success.main', mr: 1 }} />
            <Typography variant="body2">RAG Service: Ready</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'success.main', mr: 1 }} />
            <Typography variant="body2">LLM Provider: {llmProvider.toUpperCase()}</Typography>
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default ChatBot;

