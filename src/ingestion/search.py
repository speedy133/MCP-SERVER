import requests
import re
from google_play_scraper import search

def resolve_app_ids(app_name: str) -> tuple[str, str]:
    """
    Search for an app by name and return its Play Store ID and App Store ID.
    Raises ValueError if the app cannot be found on either platform.
    """
    play_store_id = None
    app_store_id = None
    
    # 1. Search Play Store
    try:
        r = requests.get(f"https://play.google.com/store/search?q={app_name}&c=apps", headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        matches = re.findall(r'/store/apps/details\?id=([a-zA-Z0-9._]+)', r.text)
        if matches:
            play_store_id = matches[0]
    except Exception as e:
        print(f"Play Store search error: {e}")

    # 2. Search App Store
    try:
        # App Store requires country code, and many apps are region specific.
        # We try US, IN, GB, AU, CA sequentially.
        countries = ['us', 'in', 'gb', 'au', 'ca']
        for country in countries:
            r = requests.get(
                f'https://itunes.apple.com/search?term={app_name}&entity=software&country={country}&limit=1',
                timeout=5
            )
            r.raise_for_status()
            data = r.json()
            if data.get('results'):
                app_store_id = str(data['results'][0]['trackId'])
                break
    except Exception as e:
        print(f"App Store search error: {e}")

    if not play_store_id and not app_store_id:
        raise ValueError(f"Could not find any app matching '{app_name}' on Play Store or App Store.")

    return play_store_id, app_store_id
