import pytest
from unittest.mock import MagicMock, call
from src.ingestion.models import Review
from src.processing.llm_client import LLMClient
from src.processing.pulse_generator import PulseGenerator, PulseReport

def test_pulse_generator_map_reduce():
    # 1. Setup mock LLM Client
    mock_llm = MagicMock(spec=LLMClient)
    
    # We will simulate multiple calls. 
    # The first call is the Map phase (extracting local themes).
    # The second call is the Reduce phase (synthesis).
    mock_llm.generate.side_effect = [
        # Map phase response
        {
            "local_themes": [
                {
                    "name": "Slow Load", 
                    "description": "App takes 10 seconds to load", 
                    "quote_text": "Takes 10 seconds to load",
                    "source": "app_store",
                    "rating": 3
                }
            ]
        },
        # Reduce phase response
        {
            "themes": [
                {"name": "Performance", "description": "App is slow", "priority": 1, "sentiment": "negative"},
            ],
            "quotes": [
                {"theme_name": "Performance", "quote_text": "Takes 10 seconds to load", "source": "app_store", "rating": 3}
            ],
            "actions": [
                "Investigate load times"
            ]
        }
    ]
    
    # 2. Setup Generator and dummy data
    generator = PulseGenerator(mock_llm)
    # 2 reviews. They both fall into the "Passives (3 stars)" bucket.
    # We set CHUNK_SIZE to 1 to force chunking logic to trigger immediately if we wanted to, 
    # but for 50 it will just be 1 chunk.
    reviews = [
        Review("app_store", "2026-07-01", 3, "Slow", "Takes 10 seconds to load"),
        Review("play_store", "2026-07-02", 3, "Ok", "It's fine but slow.")
    ]
    
    # 3. Execute
    report = generator.generate_pulse(reviews)
    
    # 4. Assert
    assert isinstance(report, PulseReport)
    assert len(report.themes) == 1
    assert report.themes[0].name == "Performance"
    
    assert len(report.quotes) == 1
    assert report.quotes[0].quote_text == "Takes 10 seconds to load"
    
    assert len(report.actions) == 1
    assert report.actions[0] == "Investigate load times"
    
    # Verify the LLM client was called twice (Once for Map, once for Reduce)
    assert mock_llm.generate.call_count == 2
    
    # Verify both calls requested JSON
    calls = mock_llm.generate.mock_calls
    for c in calls:
        assert c.kwargs.get("expect_json") is True
