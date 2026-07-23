import re
from urllib.parse import urlparse

# Basic email regex pattern
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def validate_email(email: str) -> bool:
    """
    Returns True if the email address appears valid.
    """
    return bool(EMAIL_PATTERN.match(email.strip()))

def extract_doc_id(url_or_id: str) -> str:
    """
    Extracts the Google Docs ID from a full URL or returns it if it's already an ID.
    
    Example URL: https://docs.google.com/document/d/1X2Y3Z/edit
    Example ID: 1X2Y3Z
    """
    url_or_id = url_or_id.strip()
    
    # If it doesn't look like a URL at all, assume it's a raw ID
    if not url_or_id.startswith("http"):
        # Very basic heuristic for docs IDs (usually long base64url-like strings)
        if len(url_or_id) > 20 and "/" not in url_or_id:
            return url_or_id
            
    # Try parsing as URL
    parsed = urlparse(url_or_id)
    if parsed.netloc in ["docs.google.com"]:
        parts = parsed.path.split("/")
        # The path is typically /document/d/<DOC_ID>/edit
        if "d" in parts:
            d_index = parts.index("d")
            if d_index + 1 < len(parts):
                return parts[d_index + 1]
                
    # If we couldn't extract from a docs URL but it might be an ID disguised as something else?
    # Usually it's safer to just return what we got if we couldn't match a clear pattern,
    # and let the Google API fail. However, we try one more regex match.
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url_or_id)
    if match:
        return match.group(1)
        
    return url_or_id
