import json
from dataclasses import asdict
from src.processing.pulse_generator import PulseReport
from .groq_client import GroqClient
from .prompts import DRAFTING_PROMPT

class ReportDrafter:
    """Orchestrates Groq to convert a structured PulseReport into polished prose."""
    
    def __init__(self, groq_client: GroqClient):
        self.client = groq_client
        
    def draft_report(self, report: PulseReport) -> str:
        """
        Takes a PulseReport DataClass, serializes it to JSON, 
        and uses Groq to generate a < 250 word scannable Markdown summary.
        """
        report_dict = asdict(report)
        prompt = DRAFTING_PROMPT.format(report_json=json.dumps(report_dict, indent=2))
        
        draft = self.client.generate_draft(prompt)
        
        # Enforce presence of {doc_url} placeholder (Edge Case handling)
        if "{doc_url}" not in draft:
            draft += "\n\nFull detailed report: {doc_url}"
            
        return draft
