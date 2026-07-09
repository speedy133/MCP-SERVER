from app_store_scraper import AppStore

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
    # Note: app_store_scraper expects the country and app_name. 
    # app_name doesn't strictly need to be exact for fetching by app_id, but it is required.
    app = AppStore(country="us", app_name=app_name, app_id=int(app_id))
    app.review(how_many=count)
    return app.reviews
