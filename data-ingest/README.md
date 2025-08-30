# Data Ingest Module - RSS News Fetching

This module provides comprehensive RSS news fetching functionality for financial news sources, with support for multiple categories and enhanced error handling.

## Features

- **RSS Feed Management**: Organized RSS feeds by category (business, markets, analysis, crypto, regional)
- **Multiple News Sources**: Support for major financial news outlets like Reuters, Bloomberg, CNBC, etc.
- **Enhanced Error Handling**: Retry logic, timeout handling, and comprehensive logging
- **Data Processing**: Automatic text cleaning, HTML parsing, and chunking for embeddings
- **Flexible Output**: Save as raw articles or chunked documents for vector databases

## RSS Feed Categories

### Business News
- Reuters Business
- CNBC Business
- Financial Times
- The Street

### Market News
- Bloomberg Markets
- MarketWatch Top Stories
- Yahoo Finance
- Investing.com

### Investment Analysis
- Seeking Alpha
- Motley Fool

### Cryptocurrency
- CoinDesk
- Cointelegraph
- Decrypt

### Regional News
- Asia Times Finance
- European Business Review

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test Basic Functionality

```bash
python test_fetch_news.py
```

### 3. Run Demo

```bash
python demo_rss.py
```

### 4. Windows Users

Use the provided batch or PowerShell scripts:
```bash
# Batch file
run_tests.bat

# PowerShell
.\run_tests.ps1
```

## Usage Examples

### Fetch News by Category

```python
from fetch_news import fetch_news_by_category

# Get business news
business_news = fetch_news_by_category("business", max_entries_per_feed=10)

# Get market news
market_news = fetch_news_by_category("markets", max_entries_per_feed=5)
```

### Fetch from Specific Feeds

```python
from fetch_news import fetch_news_by_feed_names

# Get news from specific sources
articles = fetch_news_by_feed_names(
    ["Reuters Business", "Bloomberg Markets"], 
    max_entries_per_feed=5
)
```

### Direct RSS URL Fetching

```python
from fetch_news import fetch_news_from_rss

# Fetch from custom RSS URLs
urls = ["https://feeds.reuters.com/reuters/businessNews"]
articles = fetch_news_from_rss(urls, max_entries_per_feed=20)
```

### Save News Data

```python
from fetch_news import ingest_category_and_save

# Save business news with automatic chunking
file_path = ingest_category_and_save("business", max_entries_per_feed=50)

# Save without chunking
file_path = ingest_category_and_save("markets", chunk=False)
```

## NewsAPI Integration

For NewsAPI functionality, set your API key as an environment variable:

```bash
# Windows
set NEWSAPI_KEY=your_api_key_here

# Linux/Mac
export NEWSAPI_KEY=your_api_key_here
```

Then use:

```python
from fetch_news import fetch_news_from_newsapi

articles = fetch_news_from_newsapi(
    api_key="your_api_key",
    query="stock market",
    page_size=50
)
```

## Configuration

### Adding New RSS Feeds

Edit `rss_config.py` to add new feeds:

```python
RSSFeed(
    name="Your Feed Name",
    url="https://your-feed-url.com/rss",
    category="business",
    description="Description of your feed"
)
```

### Customizing Feed Categories

Modify the `FEED_CATEGORIES` dictionary in `rss_config.py` to create custom categories.

## Error Handling

The module includes comprehensive error handling:

- **Retry Logic**: Automatic retries with exponential backoff
- **Timeout Handling**: Configurable request timeouts
- **Feed Validation**: Checks for valid RSS content
- **Content Filtering**: Skips articles with no meaningful content
- **Detailed Logging**: Comprehensive logging for debugging

## Output Format

### Article Structure

```json
{
    "id": "unique_article_id",
    "title": "Article Title",
    "link": "https://article-url.com",
    "published": "2024-01-01T00:00:00Z",
    "summary": "Article summary",
    "content": "Full article content",
    "source": "RSS feed URL",
    "feed_title": "Feed Name",
    "fetched_at": "2024-01-01T00:00:00Z"
}
```

### Chunked Document Structure

```json
{
    "id": "article_id_chunk_0",
    "text": "Chunked text content",
    "meta": {
        "source": "RSS feed URL",
        "title": "Article Title",
        "link": "https://article-url.com",
        "published": "2024-01-01T00:00:00Z",
        "chunk_index": 0
    }
}
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the correct directory
2. **Feed Parsing Issues**: Some RSS feeds may have malformed XML
3. **Network Timeouts**: Increase timeout values for slow feeds
4. **Missing Dependencies**: Install requirements with `pip install -r requirements.txt`

### Debug Mode

Enable debug logging by modifying `utils.py`:

```python
LOG.setLevel(logging.DEBUG)
```

## Performance Tips

- Use `max_entries_per_feed` to limit the number of articles per feed
- Enable chunking only when needed for vector databases
- Use category-based fetching for targeted news collection
- Consider implementing rate limiting for large-scale operations

## Contributing

To add new features or RSS feeds:

1. Update `rss_config.py` with new feed definitions
2. Test with `test_fetch_news.py`
3. Ensure error handling covers new scenarios
4. Update documentation as needed
