# FinSightAI Frontend

A modern React TypeScript application for the FinSightAI financial intelligence platform.

## Features

- **AI Chat Interface**: Interactive chat with RAG-powered financial AI assistant
- **News Dashboard**: Real-time financial news aggregation and insights
- **Portfolio Management**: Comprehensive portfolio tracking and analytics
- **System Dashboard**: Real-time system status and performance metrics
- **Responsive Design**: Material-UI components with modern UX
- **TypeScript**: Full type safety and enhanced developer experience

## Quick Start

### Prerequisites

- Node.js 16+ and npm
- FinSightAI backend running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

### Environment Configuration

Create a `.env.local` file in the web directory:

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── components/           # React components
│   ├── ChatBot.tsx      # AI chat interface
│   ├── NewsInsights.tsx # News dashboard
│   ├── PortfolioView.tsx# Portfolio analytics
│   └── Dashboard.tsx    # System overview
├── services/            # API client services
│   └── apiClient.ts     # Axios-based API client
├── App.tsx             # Main application component
└── index.tsx           # Application entry point
```

## Components Overview

### ChatBot
- Interactive AI chat interface
- RAG configuration controls (retrieval method, insight type, LLM provider)
- Source citation and metadata display
- Sample questions and system status

### NewsInsights
- Financial news aggregation from 24+ sources
- Category filtering (Business, Markets, Analysis, Crypto, Regional)
- Search functionality with semantic capabilities
- Article preview and source links

### PortfolioView
- Portfolio summary cards (value, change, holdings, performance)
- Interactive charts and visualizations
- Detailed holdings table with real-time data
- Performance indicators and trends

### Dashboard
- System status monitoring
- Performance metrics
- Recent activity feed
- Quick stats overview

## API Integration

The frontend connects to the FastAPI backend through:

- **RAG Endpoints**: `/query/insights`, `/query/ask`
- **News Endpoints**: `/news/latest`, `/news/category/{category}`, `/news/search`
- **Portfolio Endpoints**: `/portfolio`, `/portfolio/insights`
- **System Endpoints**: `/query/status`

## Technologies Used

- **React 18** - Modern React with hooks and functional components
- **TypeScript** - Type safety and enhanced developer experience
- **Material-UI 5** - Component library with modern design
- **Recharts** - Data visualization and charts
- **Axios** - HTTP client for API communication
- **React Router** - Client-side routing

## Development

### Available Scripts

- `npm start` - Runs the app in development mode
- `npm run build` - Builds the app for production
- `npm test` - Launches the test runner
- `npm run eject` - Ejects from Create React App (not recommended)

### API Proxy

The development server is configured to proxy API requests to `http://localhost:8000` through the `proxy` setting in `package.json`.

## Deployment

### Build for Production

```bash
npm run build
```

The build folder contains the production-ready static files.

### Deployment Options

1. **Static Hosting**: Deploy the `build` folder to any static hosting service
2. **Docker**: Create a multi-stage Docker build
3. **CDN**: Upload to S3/CloudFront or similar CDN

### Environment Variables for Production

```bash
REACT_APP_API_URL=https://your-api-domain.com
```

## Features in Detail

### AI Chat Interface

- **Multi-provider LLM support**: OpenAI GPT and Google Gemini
- **RAG configuration**: Semantic, text, and hybrid search methods
- **Insight types**: General, market analysis, portfolio advice, news summary
- **Source citations**: View and explore retrieved documents
- **Performance metrics**: Query processing time and document counts

### News Intelligence

- **Real-time updates**: Automatic refresh from 24+ financial RSS feeds
- **Smart categorization**: Business, Markets, Analysis, Crypto, Regional
- **Semantic search**: AI-powered search across financial news
- **Source diversity**: Reuters, Bloomberg, CNBC, Financial Times, and more

### Portfolio Analytics

- **Real-time data**: Live portfolio values and changes
- **Visual analytics**: Charts and performance indicators
- **Multi-asset support**: Stocks, crypto, and other securities
- **Performance tracking**: Daily changes and trends

## Troubleshooting

### Common Issues

1. **API Connection Errors**: Ensure the backend is running on http://localhost:8000
2. **CORS Issues**: The backend should be configured to allow frontend origin
3. **Build Errors**: Check TypeScript errors and resolve dependencies

### Error Handling

The frontend includes comprehensive error handling:
- API request failures show user-friendly messages
- Fallback to mock data for demonstration purposes
- Retry mechanisms for failed requests
- Loading states and error boundaries

## Contributing

1. Follow the established component structure
2. Use TypeScript for all new components
3. Include proper error handling and loading states
4. Add responsive design considerations
5. Update this README for new features

## License

Part of the FinSightAI project - see main project LICENSE.

