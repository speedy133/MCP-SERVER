import os
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Create a FastMCP server named "ReviewFetcher"
port = int(os.environ.get("PORT", 8001))
mcp = FastMCP("ReviewFetcher", port=port, host="0.0.0.0")

@mcp.tool()
def fetch_play_store_reviews(app_id: str, count: int = 100) -> list[dict]:
    """Fetch raw reviews from Google Play Store using SerpApi.
    
    Args:
        app_id: The Play Store package ID (e.g., com.whatsapp)
        count: Maximum number of reviews to fetch
    """
    if not SERPAPI_KEY:
        raise ValueError("SERPAPI_KEY environment variable is not set.")
        
    url = f"https://serpapi.com/search.json?engine=google_play_product&store=apps&product_id={app_id}&all_reviews=true&api_key={SERPAPI_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    reviews = data.get("reviews", [])
    
    # Map to the format normalizer.py expects for 'play_store'
    formatted = []
    for r in reviews[:count]:
        formatted.append({
            "content": r.get("snippet", ""),
            "title": r.get("title", ""),
            "score": r.get("rating", 0),
            "at": r.get("date", "")
        })
    return formatted

@mcp.tool()
def fetch_app_store_reviews(app_id: str, count: int = 100) -> list[dict]:
    """Fetch raw reviews from Apple App Store using SerpApi.
    
    Args:
        app_id: The Apple App Store numeric ID (e.g., 310633997)
        count: Maximum number of reviews to fetch
    """
    if not SERPAPI_KEY:
        raise ValueError("SERPAPI_KEY environment variable is not set.")
        
    url = f"https://serpapi.com/search.json?engine=apple_reviews&product_id={app_id}&api_key={SERPAPI_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    reviews = data.get("reviews", [])
    
    # Map to the format normalizer.py expects for 'app_store'
    formatted = []
    for r in reviews[:count]:
        formatted.append({
            "review": r.get("text", ""),
            "title": r.get("title", ""),
            "rating": r.get("rating", 0),
            "date": r.get("date", "")
        })
    return formatted

if __name__ == "__main__":
    # You can run this with SSE for cloud deployment, or stdio for local
    mcp.run(transport="sse")
