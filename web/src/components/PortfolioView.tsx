import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Alert,
  CircularProgress,
  Avatar,
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  Assessment,
  Refresh,
  PieChart,
} from '@mui/icons-material';
import { apiService, PortfolioData } from '../services/apiClient';

const PortfolioView: React.FC = () => {
  const [portfolioData, setPortfolioData] = useState<PortfolioData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const fetchPortfolioData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await apiService.getPortfolio();
      setPortfolioData(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch portfolio');
      // Set mock data for demonstration
      setPortfolioData(getMockPortfolioData());
    } finally {
      setLoading(false);
    }
  };

  const getMockPortfolioData = (): PortfolioData => ({
    holdings: [
      {
        symbol: 'AAPL',
        quantity: 50,
        current_price: 175.25,
        market_value: 8762.50,
        day_change: 2.15,
        day_change_percent: 1.24,
      },
      {
        symbol: 'TSLA',
        quantity: 25,
        current_price: 248.50,
        market_value: 6212.50,
        day_change: -3.75,
        day_change_percent: -1.49,
      },
      {
        symbol: 'MSFT',
        quantity: 30,
        current_price: 378.90,
        market_value: 11367.00,
        day_change: 5.20,
        day_change_percent: 1.39,
      },
      {
        symbol: 'GOOGL',
        quantity: 15,
        current_price: 142.80,
        market_value: 2142.00,
        day_change: -1.10,
        day_change_percent: -0.76,
      },
      {
        symbol: 'NVDA',
        quantity: 40,
        current_price: 455.20,
        market_value: 18208.00,
        day_change: 12.30,
        day_change_percent: 2.78,
      },
    ],
    total_value: 46692.00,
    total_change: 234.80,
    total_change_percent: 0.51,
    last_updated: new Date().toISOString(),
  });

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatPercent = (percent: number) => {
    return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress size={50} />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <AccountBalance sx={{ mr: 2 }} />
        Portfolio Overview
      </Typography>

      {/* Error Alert */}
      {error && (
        <Alert 
          severity="warning" 
          onClose={() => setError(null)} 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={fetchPortfolioData}>
              Retry
            </Button>
          }
        >
          {error}. Showing sample data for demonstration.
        </Alert>
      )}

      {portfolioData && (
        <>
          {/* Portfolio Summary Cards */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={2}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Total Value
                      </Typography>
                      <Typography variant="h5" component="div">
                        {formatCurrency(portfolioData.total_value)}
                      </Typography>
                    </Box>
                    <Avatar sx={{ bgcolor: 'primary.main' }}>
                      <AccountBalance />
                    </Avatar>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={2}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Day Change
                      </Typography>
                      <Typography 
                        variant="h5" 
                        component="div"
                        color={portfolioData.total_change >= 0 ? 'success.main' : 'error.main'}
                      >
                        {formatCurrency(portfolioData.total_change)}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        color={portfolioData.total_change >= 0 ? 'success.main' : 'error.main'}
                      >
                        {formatPercent(portfolioData.total_change_percent)}
                      </Typography>
                    </Box>
                    <Avatar sx={{ 
                      bgcolor: portfolioData.total_change >= 0 ? 'success.main' : 'error.main' 
                    }}>
                      {portfolioData.total_change >= 0 ? <TrendingUp /> : <TrendingDown />}
                    </Avatar>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={2}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Holdings
                      </Typography>
                      <Typography variant="h5" component="div">
                        {portfolioData.holdings.length}
                      </Typography>
                    </Box>
                    <Avatar sx={{ bgcolor: 'info.main' }}>
                      <PieChart />
                    </Avatar>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={2}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Performance
                      </Typography>
                      <Typography variant="h5" component="div">
                        <Chip 
                          label={portfolioData.total_change >= 0 ? 'Gaining' : 'Losing'}
                          color={portfolioData.total_change >= 0 ? 'success' : 'error'}
                          size="small"
                        />
                      </Typography>
                    </Box>
                    <Avatar sx={{ bgcolor: 'warning.main' }}>
                      <Assessment />
                    </Avatar>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Holdings Table */}
          <Paper elevation={2}>
            <Box sx={{ p: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">
                Holdings Details
              </Typography>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={fetchPortfolioData}
                disabled={loading}
              >
                Refresh
              </Button>
            </Box>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Symbol</TableCell>
                    <TableCell align="right">Quantity</TableCell>
                    <TableCell align="right">Current Price</TableCell>
                    <TableCell align="right">Market Value</TableCell>
                    <TableCell align="right">Day Change</TableCell>
                    <TableCell align="right">Day Change %</TableCell>
                    <TableCell align="center">Performance</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {portfolioData.holdings.map((holding) => (
                    <TableRow key={holding.symbol} hover>
                      <TableCell component="th" scope="row">
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ mr: 2, width: 32, height: 32 }}>
                            {holding.symbol.charAt(0)}
                          </Avatar>
                          <Typography variant="subtitle2" fontWeight="bold">
                            {holding.symbol}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="right">{holding.quantity}</TableCell>
                      <TableCell align="right">{formatCurrency(holding.current_price)}</TableCell>
                      <TableCell align="right">
                        <Typography fontWeight="bold">
                          {formatCurrency(holding.market_value)}
                        </Typography>
                      </TableCell>
                      <TableCell 
                        align="right"
                        sx={{ color: holding.day_change >= 0 ? 'success.main' : 'error.main' }}
                      >
                        {holding.day_change >= 0 ? '+' : ''}{formatCurrency(holding.day_change)}
                      </TableCell>
                      <TableCell 
                        align="right"
                        sx={{ color: holding.day_change_percent >= 0 ? 'success.main' : 'error.main' }}
                      >
                        {formatPercent(holding.day_change_percent)}
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <LinearProgress
                            variant="determinate"
                            value={Math.abs(holding.day_change_percent) * 10}
                            sx={{ 
                              width: 60, 
                              mr: 1,
                              '& .MuiLinearProgress-bar': {
                                backgroundColor: holding.day_change_percent >= 0 ? 'success.main' : 'error.main'
                              }
                            }}
                          />
                          {holding.day_change_percent >= 0 ? 
                            <TrendingUp color="success" /> : 
                            <TrendingDown color="error" />
                          }
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>

          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
            Last updated: {new Date(portfolioData.last_updated).toLocaleString()}
          </Typography>
        </>
      )}
    </Box>
  );
};

export default PortfolioView;

