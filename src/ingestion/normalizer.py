from .models import Review
import re
import emoji
from langdetect import detect, LangDetectException

def normalize(raw_reviews: list[dict], source: str) -> list[Review]:
    """
    Map source-specific fields to the unified Review schema.
    
    Args:
        raw_reviews (list[dict]): Raw reviews from the fetcher
        source (str): "play_store" or "app_store"
        
    Returns:
        list[Review]: List of normalized Review objects
    """
    normalized = []
    for raw in raw_reviews:
        if source == "play_store":
            # google-play-scraper fields
            text = raw.get("content", "")
            title = raw.get("title") or "" # Sometimes None or missing
            rating = raw.get("score", 0)
            date_obj = raw.get("at")
            date_str = date_obj if isinstance(date_obj, str) else (date_obj.isoformat() if date_obj else "")
        elif source == "app_store":
            # app-store-scraper fields
            text = raw.get("review", "")
            title = raw.get("title", "")
            rating = raw.get("rating", 0)
            date_obj = raw.get("date")
            date_str = date_obj if isinstance(date_obj, str) else (date_obj.isoformat() if date_obj else "")
        else:
            raise ValueError(f"Unknown source: {source}")

        # Truncate text if it's absurdly long (Edge case handling)
        if len(text) > 1000:
            text = text[:1000] + "..."

        if not text.strip():
            continue # Skip empty reviews
            
        # 1. Reject if less than 8 words
        if len(text.split()) < 8:
            continue
            
        # 2. Reject if contains emoji
        if emoji.emoji_count(text) > 0:
            continue
            
        # 3. Reject if Hindi language (either by langdetect or Devanagari script)
        # Check Devanagari Unicode range first for speed
        if re.search(r'[\u0900-\u097F]', text):
            continue
            
        try:
            if detect(text) == 'hi':
                continue
        except LangDetectException:
            pass # If langdetect fails (e.g. all numbers), just proceed

        normalized.append(Review(
            source=source,
            date=date_str,
            rating=rating,
            title=title,
            text=text
        ))
        
    return normalized

def deduplicate(reviews: list[Review]) -> list[Review]:
    """
    Remove duplicate reviews based on exact text match.
    Prefers the first occurrence it sees.
    """
    seen_texts = set()
    deduped = []
    
    for r in reviews:
        # Lowercase and strip for a slightly more robust deduplication
        normalized_text = r.text.strip().lower()
        if normalized_text not in seen_texts:
            seen_texts.add(normalized_text)
            deduped.append(r)
            
    return deduped
