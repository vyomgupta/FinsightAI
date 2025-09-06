import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  TextField,
  InputAdornment,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Avatar,
  Skeleton,
} from '@mui/material';
import {
  Search,
  Article,
  TrendingUp,
  Schedule,
  OpenInNew,
  Refresh,
} from '@mui/icons-material';
import { apiService, NewsArticle } from '../services/apiClient';

const NewsInsights: React.FC = () => {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { value: 'all', label: 'All News' },
    { value: 'business', label: 'Business' },
    { value: 'markets', label: 'Markets' },
    { value: 'analysis', label: 'Analysis' },
    { value: 'crypto', label: 'Crypto' },
    { value: 'regional', label: 'Regional' },
  ];

  useEffect(() => {
    fetchNews();
  }, [selectedCategory]);

  const fetchNews = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let newsData: NewsArticle[];
      
      if (selectedCategory === 'all') {
        newsData = await apiService.getLatestNews(20);
      } else {
        newsData = await apiService.getNewsByCategory(selectedCategory, 15);
      }
      
      setArticles(newsData);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch news');
      // Set mock data for demonstration
      setArticles(getMockArticles());
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchNews();
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const searchResults = await apiService.searchNews(searchQuery, 15);
      setArticles(searchResults);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Search failed');
      setArticles(getMockSearchResults());
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: string) => {
    setSelectedCategory(newValue);
    setSearchQuery('');
  };

  const formatTimestamp = (timestamp?: string) => {
    if (!timestamp) return 'Recent';
    const date = new Date(timestamp);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getCategoryColor = (category?: string) => {
    const colors: Record<string, string> = {
      business: 'primary',
      markets: 'success',
      analysis: 'warning',
      crypto: 'secondary',
      regional: 'info',
    };
    return colors[category || 'business'] || 'default';
  };

  const getMockArticles = (): NewsArticle[] => [
    {
      id: '1',
      title: 'Federal Reserve Signals Potential Rate Cuts in 2024',
      content: 'The Federal Reserve has indicated that interest rate cuts may be on the horizon as inflation continues to moderate...',
      source: 'Reuters Business',
      category: 'business',
      published: new Date().toISOString(),
      url: 'https://example.com/fed-rates',
    },
    {
      id: '2',
      title: 'Tech Stocks Rally on AI Optimism',
      content: 'Major technology stocks surged today as investors showed renewed optimism about artificial intelligence developments...',
      source: 'CNBC Markets',
      category: 'markets',
      published: new Date(Date.now() - 3600000).toISOString(),
      url: 'https://example.com/tech-rally',
    },
    {
      id: '3',
      title: 'Bitcoin Reaches New Monthly High',
      content: 'Bitcoin prices have climbed to their highest level this month, driven by institutional adoption and regulatory clarity...',
      source: 'CoinDesk',
      category: 'crypto',
      published: new Date(Date.now() - 7200000).toISOString(),
      url: 'https://example.com/bitcoin-high',
    },
  ];

  const getMockSearchResults = (): NewsArticle[] => [
    {
      id: 'search1',
      title: 'Search Results - Market Analysis',
      content: 'Your search query returned relevant financial news and analysis...',
      source: 'FinSightAI Search',
      category: 'analysis',
      published: new Date().toISOString(),
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Article sx={{ mr: 2 }} />
        Financial News & Insights
      </Typography>

      {/* Search and Filters */}
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search financial news..."
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <Button onClick={handleSearch} disabled={loading}>
                      Search
                    </Button>
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Tabs
              value={selectedCategory}
              onChange={handleTabChange}
              variant="scrollable"
              scrollButtons="auto"
            >
              {categories.map((category) => (
                <Tab
                  key={category.value}
                  value={category.value}
                  label={category.label}
                />
              ))}
            </Tabs>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Refresh />}
              onClick={fetchNews}
              disabled={loading}
            >
              Refresh
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Error Alert */}
      {error && (
        <Alert 
          severity="warning" 
          onClose={() => setError(null)} 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={fetchNews}>
              Retry
            </Button>
          }
        >
          {error}. Showing sample data for demonstration.
        </Alert>
      )}

      {/* Loading State */}
      {loading && (
        <Grid container spacing={3}>
          {[1, 2, 3, 4, 5, 6].map((item) => (
            <Grid item xs={12} md={6} lg={4} key={item}>
              <Card>
                <CardContent>
                  <Skeleton variant="text" width="60%" />
                  <Skeleton variant="text" />
                  <Skeleton variant="text" />
                  <Skeleton variant="rectangular" width="100%" height={60} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* News Articles */}
      {!loading && (
        <Grid container spacing={3}>
          {articles.map((article) => (
            <Grid item xs={12} md={6} lg={4} key={article.id}>
              <Card 
                elevation={2}
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  '&:hover': { elevation: 4, transform: 'translateY(-2px)' },
                  transition: 'all 0.3s ease-in-out',
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar sx={{ bgcolor: getCategoryColor(article.category), mr: 1, width: 32, height: 32 }}>
                      <TrendingUp />
                    </Avatar>
                    <Box>
                      <Typography variant="subtitle2" color="text.secondary">
                        {article.source}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Schedule sx={{ fontSize: 14, mr: 0.5 }} />
                        <Typography variant="caption" color="text.secondary">
                          {formatTimestamp(article.published)}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>

                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, lineHeight: 1.3 }}>
                    {article.title}
                  </Typography>

                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {article.content.length > 150 
                      ? article.content.substring(0, 150) + '...'
                      : article.content
                    }
                  </Typography>

                  {article.category && (
                    <Chip
                      label={article.category.charAt(0).toUpperCase() + article.category.slice(1)}
                      size="small"
                      color={getCategoryColor(article.category) as any}
                      variant="outlined"
                    />
                  )}
                </CardContent>

                <CardActions sx={{ p: 2, pt: 0 }}>
                  <Button
                    size="small"
                    startIcon={<Article />}
                    onClick={() => {
                      // You can add functionality to open article details
                      console.log('View article:', article.id);
                    }}
                  >
                    Read More
                  </Button>
                  {article.url && (
                    <Button
                      size="small"
                      startIcon={<OpenInNew />}
                      onClick={() => window.open(article.url, '_blank')}
                    >
                      Source
                    </Button>
                  )}
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Empty State */}
      {!loading && articles.length === 0 && (
        <Paper elevation={2} sx={{ p: 6, textAlign: 'center' }}>
          <Article sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            No articles found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {searchQuery 
              ? `No results found for "${searchQuery}". Try different keywords.`
              : 'No articles available in this category.'
            }
          </Typography>
          <Button variant="outlined" onClick={fetchNews}>
            Refresh News
          </Button>
        </Paper>
      )}
    </Box>
  );
};

export default NewsInsights;
