import logging
import time
from src.app_store_scraper import AppStore

log = logging.getLogger("WeeklyPulse")

def fetch_app_store_reviews(app_id: str, count: int = 100, app_name: str = "app") -> list[dict]:
    """
    Fetch raw reviews from the Apple App Store.
    
    Args:
        app_id (str): The Apple App Store app ID (e.g., '123456789')
        count (int): Maximum number of reviews to fetch
        app_name (str): Name of the app (needed by app-store-scraper, can be arbitrary)
        
    Returns:
        list[dict]: A list of raw review dictionaries returned by app-store-scraper.
    """
    max_retries = 3

    for attempt in range(1, max_retries + 1):
        app = AppStore(country="us", app_name=app_name, app_id=int(app_id))
        try:
            app.review(how_many=count)
            if app.reviews:
                return app.reviews
            # Got zero reviews — may be a transient empty response, retry
            log.warning("  App Store attempt %d/%d returned 0 reviews.", attempt, max_retries)
        except Exception as e:
            log.warning("  App Store attempt %d/%d failed: %s", attempt, max_retries, e)

        if attempt < max_retries:
            wait = 2 ** attempt  # 2s, 4s
            log.info("  Retrying App Store fetch in %ds...", wait)
            time.sleep(wait)

    log.warning("  All %d App Store fetch attempts exhausted — returning empty list.", max_retries)
    return []

