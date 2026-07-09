import json
from pathlib import Path
from datetime import datetime
import pytest

from src.ingestion.models import Review
from src.ingestion.normalizer import normalize, deduplicate

@pytest.fixture
def sample_raw_data():
    data_path = Path(__file__).parent.parent / "data" / "sample_reviews.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_normalize_play_store(sample_raw_data):
    # Filter play store data and convert 'at' to datetime object to simulate google-play-scraper output
    play_data = [d.copy() for d in sample_raw_data if d["source"] == "play_store"]
    for d in play_data:
        if "at" in d:
            d["at"] = datetime.fromisoformat(d["at"].replace('Z', '+00:00'))

    normalized = normalize(play_data, source="play_store")
    
    # We have 5 play store reviews in sample data.
    # - 2 are normal duplicates (so both pass normalization, caught later by dedup)
    # - 1 is < 8 words (filtered)
    # - 1 is Hindi (filtered)
    # So 3 reviews should pass normalization. (Wait, let's recount.
    # Play store has:
    # 1: Great app... (14 words) -> passes
    # 2: Onboarding was super... (8 words) -> passes
    # 3: Great app... (duplicate, 14 words) -> passes
    # 4: Too short. (2 words) -> filtered
    # 5: यह ऐप बहुत... (Hindi) -> filtered
    # Total passing: 3
    assert len(normalized) == 3
    for rev in normalized:
        assert isinstance(rev, Review)
        assert rev.source == "play_store"
        assert type(rev.rating) == int
        assert rev.text != "" # No empty text

def test_normalize_app_store(sample_raw_data):
    # Filter app store data and convert 'date' to datetime object to simulate app-store-scraper output
    app_data = [d.copy() for d in sample_raw_data if d["source"] == "app_store"]
    for d in app_data:
        if "date" in d:
            d["date"] = datetime.fromisoformat(d["date"].replace('Z', '+00:00'))

    normalized = normalize(app_data, source="app_store")
    
    # We have 4 app store reviews in sample.
    # 1: The statements page... (13 words) -> passes
    # 2: I love the new... (12 words) -> passes
    # 3: Empty text -> filtered
    # 4: Emoji text "This is a very good app indeed 👍" (8 words + emoji) -> filtered
    # Total passing: 2
    assert len(normalized) == 2
    for rev in normalized:
        assert rev.source == "app_store"
        assert rev.text != ""

def test_deduplicate(sample_raw_data):
    # Create fake reviews with some duplicates
    reviews = [
        Review("play_store", "2026-06-25", 2, "Title", "This is a test."),
        Review("app_store", "2026-06-26", 5, "", "Another review."),
        Review("play_store", "2026-06-27", 3, "", "This is a test.") # Duplicate
    ]
    
    deduped = deduplicate(reviews)
    assert len(deduped) == 2
    assert deduped[0].text == "This is a test."
    assert deduped[1].text == "Another review."
