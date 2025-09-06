# data_ingest/cron_jobs.py
import time
import schedule
from .fetch_portfolio import mock_portfolio
from .fetch_news import ingest_rss_and_save
from .utils import LOG

def run_periodic_ingestion(rss_feeds, interval_minutes: int = 30, demo: bool = True):
    LOG.info("Starting periodic ingestion scheduler")

    def job():
        LOG.info("Running scheduled ingestion job")
        try:
            from .fetch_portfolio import fetch_portfolio_from_api, ingest_portfolio_and_save
            from api.utils.config import get_portfolio_api_config # Assuming this config exists or will be created

            portfolio_config = get_portfolio_api_config()
            portfolio_api_url = portfolio_config.get("url")
            portfolio_api_key = portfolio_config.get("api_key")

            if portfolio_api_url:
                LOG.info("Fetching portfolio from actual API")
                p = fetch_portfolio_from_api(api_url=portfolio_api_url, api_key=portfolio_api_key)
                ingest_portfolio_and_save(p, filename=f"portfolio_{int(time.time())}.json")
            else:
                LOG.warning("Portfolio API URL not configured. Skipping actual portfolio ingestion.")

            ingest_rss_and_save(rss_feeds, filename=f"rss_{int(time.time())}.json")
        except Exception as e:
            LOG.exception(f"Scheduled ingestion failed: {e}")

    schedule.every(interval_minutes).minutes.do(job)
    job()  # run once immediately
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    example_rss = [
        'https://economictimes.indiatimes.com/feeds/rssfeedstopstories.cms',
        'https://www.moneycontrol.com/rss/MCtopnews.xml',
        'https://www.reuters.com/finance/markets/rss'
    ]
    run_periodic_ingestion(example_rss, interval_minutes=30, demo=False)
