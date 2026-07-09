import pytest
from unittest.mock import MagicMock
from src.processing.pulse_generator import PulseReport, Theme, Quote
from src.drafting.groq_client import GroqClient
from src.drafting.drafter import ReportDrafter

def test_draft_report_includes_doc_url():
    # 1. Setup mock Groq Client
    mock_groq = MagicMock(spec=GroqClient)
    
    # Simulate a response that FORGETS the {doc_url} placeholder
    mock_groq.generate_draft.return_value = "This is a great weekly pulse report. The end."
    
    # 2. Setup Drafter and dummy data
    drafter = ReportDrafter(mock_groq)
    
    dummy_report = PulseReport(
        generated_date="2026-07-07",
        themes=[Theme("Bug", "Crash on startup", 1, "negative")],
        quotes=[Quote("Bug", "App crashes instantly", "play_store", 1)],
        actions=["Fix startup crash"]
    )
    
    # 3. Execute
    draft = drafter.draft_report(dummy_report)
    
    # 4. Assert
    assert "{doc_url}" in draft
    assert "This is a great weekly pulse report" in draft
    mock_groq.generate_draft.assert_called_once()
    
def test_draft_report_keeps_existing_doc_url():
    # 1. Setup mock Groq Client
    mock_groq = MagicMock(spec=GroqClient)
    
    # Simulate a response that correctly includes the placeholder
    mock_groq.generate_draft.return_value = "Weekly pulse. See here: {doc_url}"
    
    # 2. Setup Drafter
    drafter = ReportDrafter(mock_groq)
    
    dummy_report = PulseReport(
        generated_date="2026-07-07",
        themes=[],
        quotes=[],
        actions=[]
    )
    
    # 3. Execute
    draft = drafter.draft_report(dummy_report)
    
    # 4. Assert
    assert draft == "Weekly pulse. See here: {doc_url}"
    # Ensure it didn't append a second one
    assert draft.count("{doc_url}") == 1
