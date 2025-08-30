"""
RSS Feed Configuration for Financial News Sources
"""
from typing import Dict, List, NamedTuple

class RSSFeed(NamedTuple):
    name: str
    url: str
    category: str
    description: str
    max_entries: int = 50

# Major Financial News Sources
MAJOR_NEWS_FEEDS = [
    RSSFeed(
        name="Reuters Business",
        url="https://feeds.reuters.com/reuters/businessNews",
        category="business",
        description="Reuters business and financial news"
    ),
    RSSFeed(
        name="Bloomberg Markets",
        url="https://feeds.bloomberg.com/markets/news.rss",
        category="markets",
        description="Bloomberg market news and analysis"
    ),
    RSSFeed(
        name="CNBC Business",
        url="https://www.cnbc.com/id/100003114/device/rss/rss.html",
        category="business",
        description="CNBC business news and market updates"
    ),
    RSSFeed(
        name="MarketWatch Top Stories",
        url="https://feeds.marketwatch.com/marketwatch/topstories/",
        category="markets",
        description="MarketWatch top financial stories"
    ),
    RSSFeed(
        name="Financial Times",
        url="https://www.ft.com/rss/home",
        category="business",
        description="Financial Times global business news"
    ),
    RSSFeed(
        name="Yahoo Finance",
        url="https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC,^DJI,^IXIC&region=US&lang=en-US",
        category="markets",
        description="Yahoo Finance market headlines"
    ),
]

# Specialized Financial News
SPECIALIZED_FEEDS = [
    RSSFeed(
        name="Seeking Alpha",
        url="https://seekingalpha.com/feed.xml",
        category="analysis",
        description="Investment analysis and stock market insights"
    ),
    RSSFeed(
        name="Investing.com",
        url="https://www.investing.com/rss/news_301.rss",
        category="markets",
        description="Investing.com financial news"
    ),
    RSSFeed(
        name="The Street",
        url="https://www.thestreet.com/.rss/full",
        category="business",
        description="The Street financial news and analysis"
    ),
    RSSFeed(
        name="Motley Fool",
        url="https://www.fool.com/feed/",
        category="analysis",
        description="Motley Fool investment advice and analysis"
    ),
]

# Cryptocurrency and Fintech
CRYPTO_FEEDS = [
    RSSFeed(
        name="CoinDesk",
        url="https://www.coindesk.com/arc/outboundfeeds/rss/",
        category="crypto",
        description="CoinDesk cryptocurrency news"
    ),
    RSSFeed(
        name="Cointelegraph",
        url="https://cointelegraph.com/rss",
        category="crypto",
        description="Cointelegraph crypto and blockchain news"
    ),
    RSSFeed(
        name="Decrypt",
        url="https://decrypt.co/feed",
        category="crypto",
        description="Decrypt cryptocurrency and DeFi news"
    ),
]

# Regional Financial News
REGIONAL_FEEDS = [
    RSSFeed(
        name="Asia Times Finance",
        url="https://asiatimes.com/category/finance/feed/",
        category="regional",
        description="Asian financial markets and business news"
    ),
    RSSFeed(
        name="European Business Review",
        url="https://www.europeanbusinessreview.com/feed/",
        category="regional",
        description="European business and financial news"
    ),
]

# All feeds combined
ALL_FEEDS = MAJOR_NEWS_FEEDS + SPECIALIZED_FEEDS + CRYPTO_FEEDS + REGIONAL_FEEDS

# Feed categories
FEED_CATEGORIES = {
    "business": [feed for feed in ALL_FEEDS if feed.category == "business"],
    "markets": [feed for feed in ALL_FEEDS if feed.category == "markets"],
    "analysis": [feed for feed in ALL_FEEDS if feed.category == "analysis"],
    "crypto": [feed for feed in ALL_FEEDS if feed.category == "crypto"],
    "regional": [feed for feed in ALL_FEEDS if feed.category == "regional"],
}

def get_feeds_by_category(category: str) -> List[RSSFeed]:
    """Get feeds by category"""
    return FEED_CATEGORIES.get(category, [])

def get_feeds_by_name(names: List[str]) -> List[RSSFeed]:
    """Get feeds by name"""
    return [feed for feed in ALL_FEEDS if feed.name in names]

def get_all_feed_urls() -> List[str]:
    """Get all RSS feed URLs"""
    return [feed.url for feed in ALL_FEEDS]

def get_feeds_for_testing() -> List[RSSFeed]:
    """Get a small subset of feeds for testing purposes"""
    return [
        RSSFeed(
            name="Reuters Business (Test)",
            url="https://feeds.reuters.com/reuters/businessNews",
            category="business",
            description="Reuters business news for testing",
            max_entries=5
        ),
        RSSFeed(
            name="Bloomberg Markets (Test)",
            url="https://feeds.bloomberg.com/markets/news.rss",
            category="markets",
            description="Bloomberg markets for testing",
            max_entries=5
        ),
    ]

if __name__ == "__main__":
    print("RSS Feed Configuration")
    print("=" * 50)
    print(f"Total feeds: {len(ALL_FEEDS)}")
    print(f"Categories: {list(FEED_CATEGORIES.keys())}")
    
    for category, feeds in FEED_CATEGORIES.items():
        print(f"\n{category.upper()} ({len(feeds)} feeds):")
        for feed in feeds:
            print(f"  - {feed.name}: {feed.url}")
