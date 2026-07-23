import os
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

from .tools.gmail import send_email_impl, draft_email_impl, EmailSchema
from .tools.docs import (
    append_to_google_doc_impl, DocsAppendSchema,
    create_document_impl, DocsCreateSchema,
)

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

@mcp.tool()
def send_email(
    to: list[str],
    subject: str,
    body: str,
    cc: list[str] = None,
    bcc: list[str] = None,
    body_type: str = "plain"
) -> dict:
    """
    Send an email immediately via the authenticated Gmail account.
    """
    if body_type not in ["plain", "html"]:
        raise ValueError("body_type must be either 'plain' or 'html'")
        
    params = EmailSchema(
        to=to, subject=subject, body=body, cc=cc, bcc=bcc, body_type=body_type
    )
    return send_email_impl(params)

@mcp.tool()
def draft_email(
    to: list[str],
    subject: str,
    body: str,
    cc: list[str] = None,
    bcc: list[str] = None,
    body_type: str = "plain"
) -> dict:
    """
    Create a draft in the authenticated Gmail account without sending.
    """
    if body_type not in ["plain", "html"]:
        raise ValueError("body_type must be either 'plain' or 'html'")
        
    params = EmailSchema(
        to=to, subject=subject, body=body, cc=cc, bcc=bcc, body_type=body_type
    )
    return draft_email_impl(params)

@mcp.tool()
def create_document(
    title: str,
    content: str,
) -> dict:
    """
    Create a new Google Doc with the given title and body content.
    """
    params = DocsCreateSchema(title=title, content=content)
    return create_document_impl(params)

@mcp.tool()
def append_to_google_doc(
    document_id: str,
    content: str,
    add_timestamp_heading: bool = False,
    leading_newline: bool = True
) -> dict:
    """
    Append text content to the end of an existing Google Doc.
    """
    params = DocsAppendSchema(
        document_id=document_id,
        content=content,
        add_timestamp_heading=add_timestamp_heading,
        leading_newline=leading_newline
    )
    return append_to_google_doc_impl(params)

if __name__ == "__main__":
    from .auth import get_credentials
    import sys
    try:
        get_credentials()
    except Exception as e:
        print(f"Failed to initialize credentials: {e}", file=sys.stderr)

    # You can run this with SSE for cloud deployment, or stdio for local
    mcp.run(transport="sse")
