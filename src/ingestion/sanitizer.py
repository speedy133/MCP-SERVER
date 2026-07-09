import re
from .models import Review

# Pre-compiled regex patterns for PII detection
PII_PATTERNS = {
    # Matches emails like user@example.com
    "EMAIL": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    
    # Matches phone numbers in various formats (e.g., +1-555-123-4567, (555) 123-4567)
    "PHONE": re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
    
    # Matches social media handles like @username
    "HANDLE": re.compile(r'(?<!\w)@[\w.-]+\b'),
    
    # Matches potential Device IDs / UUIDs
    "UUID": re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'),
    
    # Matches common IP addresses (IPv4)
    "IP_ADDRESS": re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
}

def sanitize(reviews: list[Review]) -> list[Review]:
    """
    Scrub PII (Personally Identifiable Information) from a list of reviews.
    Replaces matched PII with '[REDACTED]'.
    
    Args:
        reviews (list[Review]): List of normalized reviews.
        
    Returns:
        list[Review]: List of reviews with PII stripped from the text and title.
    """
    sanitized_reviews = []
    
    for review in reviews:
        clean_text = review.text
        clean_title = review.title
        
        for name, pattern in PII_PATTERNS.items():
            clean_text = pattern.sub("[REDACTED]", clean_text)
            clean_title = pattern.sub("[REDACTED]", clean_title)
            
        sanitized_reviews.append(
            Review(
                source=review.source,
                date=review.date,
                rating=review.rating,
                title=clean_title,
                text=clean_text
            )
        )
        
    return sanitized_reviews
