from google_play_scraper import reviews, Sort

def fetch_play_store_reviews(app_id: str, count: int = 100) -> list[dict]:
    """
    Fetch raw reviews from the Google Play Store.
    
    Args:
        app_id (str): The Google Play Store app ID (e.g., 'com.example.app')
        count (int): Maximum number of reviews to fetch
        
    Returns:
        list[dict]: A list of raw review dictionaries returned by google-play-scraper.
    """
    result, continuation_token = reviews(
        app_id,
        lang='en', # defaults to 'en'
        country='us', # defaults to 'us'
        sort=Sort.NEWEST, # defaults to Sort.NEWEST
        count=count
    )
    return result
