# data_ingest/fetch_news.py
from typing import List, Dict, Any, Optional
import feedparser
import requests
from datetime import datetime, timedelta
import time
from pathlib import Path

# Import utilities with fallback for standalone execution
try:
    from .utils import LOG, DATA_DIR
    from .clean_data import prepare_article_for_embeddings
    # Import RSS configuration
    try:
        from .rss_config import get_feeds_by_category, get_feeds_by_name, get_all_feed_urls, get_feeds_for_testing
    except ImportError:
        # Fallback if rss_config is not available
        get_feeds_by_category = lambda x: []
        get_feeds_by_name = lambda x: []
        get_all_feed_urls = lambda: []
        get_feeds_for_testing = lambda: []
except ImportError:
    # Fallback for standalone execution
    from utils import LOG, DATA_DIR
    from clean_data import prepare_article_for_embeddings
    try:
        from rss_config import get_feeds_by_category, get_feeds_by_name, get_all_feed_urls, get_feeds_for_testing
    except ImportError:
        # Fallback if rss_config is not available
        get_feeds_by_category = lambda x: []
        get_feeds_by_name = lambda x: []
        get_all_feed_urls = lambda: []
        get_feeds_for_testing = lambda: []


def fetch_news_from_rss(rss_urls: List[str], max_entries_per_feed: int = 50, 
                        timeout: int = 30, retry_attempts: int = 3) -> List[Dict[str, Any]]:
    """
    Fetch news from RSS feeds with enhanced error handling and retry logic
    
    Args:
        rss_urls: List of RSS feed URLs
        max_entries_per_feed: Maximum number of entries to fetch per feed
        timeout: Request timeout in seconds
        retry_attempts: Number of retry attempts for failed feeds
    
    Returns:
        List of article dictionaries
    """
    LOG.info(f"Fetching RSS feeds ({len(rss_urls)} feeds)")
    articles = []
    
    for url in rss_urls:
        for attempt in range(retry_attempts):
            try:
                LOG.debug(f"Fetching RSS feed: {url} (attempt {attempt + 1})")
                
                # Parse RSS feed
                d = feedparser.parse(url)
                
                if d.bozo:
                    LOG.warning(f"Feed parse issue for {url}: {d.bozo_exception}")
                
                # Check if feed has entries
                if not d.entries:
                    LOG.warning(f"No entries found in RSS feed: {url}")
                    break
                
                LOG.info(f"Found {len(d.entries)} entries in {url}")
                
                # Process entries
                for entry in d.entries[:max_entries_per_feed]:
                    try:
                        published = entry.get("published") or entry.get("updated") or entry.get("pubDate")
                        
                        # Clean and validate content
                        title = entry.get("title", "").strip()
                        summary = entry.get("summary", "").strip()
                        content = entry.get("content", [])
                        
                        if content:
                            # Handle different content formats
                            if isinstance(content, list):
                                content_text = " ".join([c.get("value", "") for c in content])
                            else:
                                content_text = str(content)
                        else:
                            content_text = summary
                        
                        # Skip articles with no meaningful content
                        if not title and not content_text:
                            continue
                        
                        article = {
                            "id": entry.get("id") or entry.get("link") or f"{url}_{hash(title)}",
                            "title": title,
                            "link": entry.get("link", ""),
                            "published": published,
                            "summary": summary,
                            "content": content_text,
                            "source": url,
                            "feed_title": d.feed.get("title", ""),
                            "fetched_at": datetime.now().isoformat(),
                        }
                        articles.append(article)
                        
                    except Exception as e:
                        LOG.warning(f"Error processing RSS entry from {url}: {e}")
                        continue
                
                # Successfully processed this feed
                break
                
            except Exception as e:
                LOG.warning(f"Error fetching RSS {url} (attempt {attempt + 1}): {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    LOG.error(f"Failed to fetch RSS {url} after {retry_attempts} attempts")
    
    LOG.info(f"Successfully fetched {len(articles)} articles from RSS feeds")
    return articles


def fetch_news_from_newsapi(api_key: str, query: str = "stock market", 
                           from_date: Optional[str] = None, page_size: int = 100,
                           timeout: int = 30) -> List[Dict[str, Any]]:
    """
    Fetch news from NewsAPI with enhanced error handling
    
    Args:
        api_key: NewsAPI API key
        query: Search query
        from_date: Start date for search (YYYY-MM-DD format)
        page_size: Number of articles per page (max 100)
        timeout: Request timeout in seconds
    
    Returns:
        List of article dictionaries
    """
    LOG.info(f"Fetching news from NewsAPI with query: '{query}'")
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "pageSize": min(page_size, 100),  # NewsAPI max is 100
        "language": "en",
        "sortBy": "publishedAt",
    }
    
    if from_date:
        params["from"] = from_date
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        
        payload = resp.json()
        
        if payload.get("status") != "ok":
            LOG.error(f"NewsAPI error: {payload.get('message', 'Unknown error')}")
            return []
        
        total_results = payload.get("totalResults", 0)
        LOG.info(f"NewsAPI found {total_results} total articles for query: '{query}'")
        
        items = []
        for art in payload.get("articles", []):
            try:
                # Clean and validate article data
                title = art.get("title", "").strip()
                content = art.get("content", "").strip()
                description = art.get("description", "").strip()
                
                # Skip articles with no meaningful content
                if not title and not content and not description:
                    continue
                
                items.append({
                    "id": art.get("url") or f"newsapi_{hash(title)}",
                    "title": title,
                    "link": art.get("url"),
                    "published": art.get("publishedAt"),
                    "summary": description,
                    "content": content,
                    "source": art.get("source", {}).get("name", "NewsAPI"),
                    "fetched_at": datetime.now().isoformat(),
                })
                
            except Exception as e:
                LOG.warning(f"Error processing NewsAPI article: {e}")
                continue
        
        LOG.info(f"Successfully processed {len(items)} articles from NewsAPI")
        return items
        
    except requests.exceptions.RequestException as e:
        LOG.error(f"Request error fetching from NewsAPI: {e}")
        return []
    except Exception as e:
        LOG.error(f"Unexpected error fetching from NewsAPI: {e}")
        return []


def fetch_news_by_category(category: str, max_entries_per_feed: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch news from RSS feeds by category using the RSS configuration
    
    Args:
        category: News category (business, markets, analysis, crypto, regional)
        max_entries_per_feed: Maximum entries per feed
    
    Returns:
        List of article dictionaries
    """
    feeds = get_feeds_by_category(category)
    if not feeds:
        LOG.warning(f"No RSS feeds found for category: {category}")
        return []
    
    urls = [feed.url for feed in feeds]
    LOG.info(f"Fetching {len(urls)} RSS feeds for category: {category}")
    
    return fetch_news_from_rss(urls, max_entries_per_feed)


def fetch_news_by_feed_names(feed_names: List[str], max_entries_per_feed: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch news from specific RSS feeds by name
    
    Args:
        feed_names: List of feed names to fetch from
        max_entries_per_feed: Maximum entries per feed
    
    Returns:
        List of article dictionaries
    """
    feeds = get_feeds_by_name(feed_names)
    if not feeds:
        LOG.warning(f"No RSS feeds found for names: {feed_names}")
        return []
    
    urls = [feed.url for feed in feeds]
    LOG.info(f"Fetching {len(urls)} RSS feeds: {feed_names}")
    
    return fetch_news_from_rss(urls, max_entries_per_feed)


def ingest_rss_and_save(rss_urls: List[str], filename: str = "rss_articles.json", 
                        chunk: bool = True, category: str = None) -> Path:
    """
    Ingest RSS feeds and save to file
    
    Args:
        rss_urls: List of RSS feed URLs
        filename: Output filename
        chunk: Whether to chunk articles for embeddings
        category: Optional category for filename
    
    Returns:
        Path to saved file
    """
    articles = fetch_news_from_rss(rss_urls)
    
    if not articles:
        LOG.warning("No articles fetched, creating empty file")
        articles = []
    
    if chunk:
        docs = []
        for a in articles:
            docs.extend(prepare_article_for_embeddings(a))
        try:
            from .utils import save_json
        except ImportError:
            from utils import save_json
        save_json(docs, DATA_DIR / filename)
        LOG.info(f"Saved {len(docs)} chunked documents to {filename}")
    else:
        try:
            from .utils import save_json
        except ImportError:
            from utils import save_json
        save_json(articles, DATA_DIR / filename)
        LOG.info(f"Saved {len(articles)} articles to {filename}")
    
    return DATA_DIR / filename


def ingest_newsapi_and_save(api_key: str, query: str = "stock market", 
                           filename: str = "newsapi_articles.json", chunk: bool = True) -> Path:
    """
    Ingest NewsAPI and save to file
    
    Args:
        api_key: NewsAPI API key
        query: Search query
        filename: Output filename
        chunk: Whether to chunk articles for embeddings
    
    Returns:
        Path to saved file
    """
    articles = fetch_news_from_newsapi(api_key=api_key, query=query)
    
    if not articles:
        LOG.warning("No articles fetched from NewsAPI, creating empty file")
        articles = []
    
    if chunk:
        docs = []
        for a in articles:
            docs.extend(prepare_article_for_embeddings(a))
        try:
            from .utils import save_json
        except ImportError:
            from utils import save_json
        save_json(docs, DATA_DIR / filename)
        LOG.info(f"Saved {len(docs)} chunked documents to {filename}")
    else:
        try:
            from .utils import save_json
        except ImportError:
            from utils import save_json
        save_json(articles, DATA_DIR / filename)
        LOG.info(f"Saved {len(articles)} articles to {filename}")
    
    return DATA_DIR / filename


def ingest_category_and_save(category: str, filename: str = None, 
                           max_entries_per_feed: int = 50, chunk: bool = True) -> Path:
    """
    Ingest news by category and save to file
    
    Args:
        category: News category
        filename: Output filename (auto-generated if None)
        max_entries_per_feed: Maximum entries per feed
        chunk: Whether to chunk articles for embeddings
    
    Returns:
        Path to saved file
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{category}_articles_{timestamp}.json"
    
    articles = fetch_news_by_category(category, max_entries_per_feed)
    
    if chunk:
        docs = []
        for a in articles:
            docs.extend(prepare_article_for_embeddings(a))
        try:
            from .utils import save_json
        except ImportError:
            from utils import save_json
        save_json(docs, DATA_DIR / filename)
        LOG.info(f"Saved {len(docs)} chunked documents to {filename}")
    else:
        try:
            from .utils import save_json
        except ImportError:
            from utils import save_json
        save_json(articles, DATA_DIR / filename)
        LOG.info(f"Saved {len(articles)} articles to {filename}")
    
    return DATA_DIR / filename
