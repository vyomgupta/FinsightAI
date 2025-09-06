import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, AppBar, Toolbar, Typography, Container, Tabs, Tab } from '@mui/material';
import { TrendingUp, Chat, Assessment, Dashboard as DashboardIcon } from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';

// Import components
import ChatBot from './components/ChatBot';
import NewsInsights from './components/NewsInsights';
import PortfolioView from './components/PortfolioView';
import Dashboard from './components/Dashboard';

function App() {
  const location = useLocation();
  const navigate = useNavigate();

  // Determine current tab based on route
  const getCurrentTab = () => {
    const path = location.pathname;
    if (path.startsWith('/chat')) return 0;
    if (path.startsWith('/news')) return 1;
    if (path.startsWith('/portfolio')) return 2;
    if (path.startsWith('/dashboard')) return 3;
    return 0;
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    const routes = ['/chat', '/news', '/portfolio', '/dashboard'];
    navigate(routes[newValue]);
  };

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* App Header */}
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <TrendingUp sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            FinSightAI
          </Typography>
          <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
            Financial Intelligence Platform
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Navigation Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'white' }}>
        <Container maxWidth="xl">
          <Tabs
            value={getCurrentTab()}
            onChange={handleTabChange}
            aria-label="FinSightAI navigation"
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab
              icon={<Chat />}
              label="AI Chat"
              iconPosition="start"
              sx={{ minHeight: 60 }}
            />
            <Tab
              icon={<Assessment />}
              label="News & Insights"
              iconPosition="start"
              sx={{ minHeight: 60 }}
            />
            <Tab
              icon={<TrendingUp />}
              label="Portfolio"
              iconPosition="start"
              sx={{ minHeight: 60 }}
            />
            <Tab
              icon={<DashboardIcon />}
              label="Dashboard"
              iconPosition="start"
              sx={{ minHeight: 60 }}
            />
          </Tabs>
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
        <Routes>
          <Route path="/" element={<Navigate to="/chat" replace />} />
          <Route path="/chat" element={<ChatBot />} />
          <Route path="/news" element={<NewsInsights />} />
          <Route path="/portfolio" element={<PortfolioView />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="*" element={<Navigate to="/chat" replace />} />
        </Routes>
      </Container>
    </Box>
  );
}

export default App;
