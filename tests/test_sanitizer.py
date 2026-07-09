import pytest
from src.ingestion.models import Review
from src.ingestion.sanitizer import sanitize

def test_sanitize_emails():
    reviews = [
        Review("play_store", "2026-07-01", 5, "Support email", "Contact me at john.doe@example.com for more info!"),
        Review("app_store", "2026-07-02", 1, "test@test.co.uk", "My email is test@test.co.uk.")
    ]
    sanitized = sanitize(reviews)
    
    assert "john.doe@example.com" not in sanitized[0].text
    assert "[REDACTED]" in sanitized[0].text
    
    assert "test@test.co.uk" not in sanitized[1].title
    assert "[REDACTED]" in sanitized[1].title
    assert "test@test.co.uk" not in sanitized[1].text

def test_sanitize_phone_numbers():
    reviews = [
        Review("play_store", "2026-07-01", 3, "Call me", "Call +1-555-123-4567 to resolve this."),
        Review("app_store", "2026-07-02", 1, "No title", "My number: (555) 987-6543 please fix.")
    ]
    sanitized = sanitize(reviews)
    
    assert "+1-555-123-4567" not in sanitized[0].text
    assert "[REDACTED]" in sanitized[0].text
    
    assert "(555) 987-6543" not in sanitized[1].text
    assert "[REDACTED]" in sanitized[1].text

def test_sanitize_handles():
    reviews = [
        Review("play_store", "2026-07-01", 5, "Twitter", "Follow my handle @super_user99 for updates."),
        Review("app_store", "2026-07-02", 5, "Insta", "Hit me up @john.doe")
    ]
    sanitized = sanitize(reviews)
    
    assert "@super_user99" not in sanitized[0].text
    assert "[REDACTED]" in sanitized[0].text
    
    assert "@john.doe" not in sanitized[1].text
    assert "[REDACTED]" in sanitized[1].text
    
def test_sanitize_uuid_and_ip():
    reviews = [
        Review("play_store", "2026-07-01", 1, "Crash", "Crashed on device id 123e4567-e89b-12d3-a456-426614174000."),
        Review("app_store", "2026-07-02", 2, "Network", "Failed to connect to 192.168.1.100.")
    ]
    sanitized = sanitize(reviews)
    
    assert "123e4567-e89b-12d3-a456-426614174000" not in sanitized[0].text
    assert "[REDACTED]" in sanitized[0].text
    
    assert "192.168.1.100" not in sanitized[1].text
    assert "[REDACTED]" in sanitized[1].text
