# data_ingest/fetch_news.py
from typing import List, Dict, Any, Optional
import feedparser
import requests
from .utils import LOG, DATA_DIR
from .clean_data import prepare_article_for_embeddings


def fetch_news_from_rss(rss_urls: List[str], max_entries_per_feed: int = 50) -> List[Dict[str, Any]]:
    LOG.info(f"Fetching RSS feeds ({len(rss_urls)} feeds)")
    articles = []
    for url in rss_urls:
        try:
            d = feedparser.parse(url)
            if d.bozo:
                LOG.warning(f"Feed parse issue for {url}: {d.bozo_exception}")
            for entry in d.entries[:max_entries_per_feed]:
                published = entry.get("published") or entry.get("updated") or entry.get("pubDate")
                article = {
                    "id": entry.get("id") or entry.get("link"),
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": published,
                    "summary": entry.get("summary", ""),
                    "content": " ".join([c.get("value", "") for c in entry.get("content", [])]) if entry.get("content") else entry.get("summary", ""),
                    "source": url,
                }
                articles.append(article)
        except Exception as e:
            LOG.exception(f"Error fetching RSS {url}: {e}")
    LOG.info(f"Fetched {len(articles)} articles from RSS feeds")
    return articles


def fetch_news_from_newsapi(api_key: str, query: str = "stock market", from_date: Optional[str] = None, page_size: int = 100) -> List[Dict[str, Any]]:
    LOG.info("Fetching news from NewsAPI")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "pageSize": page_size,
        "language": "en",
        "sortBy": "publishedAt",
    }
    if from_date:
        params["from"] = from_date
    headers = {"Authorization": api_key}
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    payload = resp.json()
    items = []
    for art in payload.get("articles", []):
        items.append(
            {
                "id": art.get("url"),
                "title": art.get("title"),
                "link": art.get("url"),
                "published": art.get("publishedAt"),
                "summary": art.get("description") or "",
                "content": art.get("content") or "",
                "source": art.get("source", {}).get("name"),
            }
        )
    LOG.info(f"NewsAPI returned {len(items)} articles")
    return items


def ingest_rss_and_save(rss_urls: List[str], filename: str = "rss_articles.json", chunk: bool = True):
    articles = fetch_news_from_rss(rss_urls)
    if chunk:
        docs = []
        for a in articles:
            docs.extend(prepare_article_for_embeddings(a))
        from .utils import save_json

        save_json(docs, DATA_DIR / filename)
    else:
        from .utils import save_json

        save_json(articles, DATA_DIR / filename)
    return DATA_DIR / filename


def ingest_newsapi_and_save(api_key: str, query: str = "stock market", filename: str = "newsapi_articles.json", chunk: bool = True):
    articles = fetch_news_from_newsapi(api_key=api_key, query=query)
    if chunk:
        docs = []
        for a in articles:
            docs.extend(prepare_article_for_embeddings(a))
        from .utils import save_json

        save_json(docs, DATA_DIR / filename)
    else:
        from .utils import save_json

        save_json(articles, DATA_DIR / filename)
    return DATA_DIR / filename
