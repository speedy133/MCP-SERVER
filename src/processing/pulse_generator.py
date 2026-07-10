import json
from dataclasses import dataclass, asdict
from datetime import datetime
from src.ingestion.models import Review
from src.drafting.groq_client import GroqClient
from .prompts import LOCAL_ANALYSIS_PROMPT, SYNTHESIS_PROMPT

@dataclass
class Theme:
    name: str
    description: str
    priority: int
    sentiment: str

@dataclass
class Quote:
    theme_name: str
    quote_text: str
    source: str
    rating: int

@dataclass
class PulseReport:
    generated_date: str
    themes: list[Theme]
    quotes: list[Quote]
    actions: list[str]

class PulseGenerator:
    """Orchestrates the Map-Reduce LLM analysis for large volumes of reviews."""
    
    CHUNK_SIZE = 50
    
    def __init__(self, llm_client: GroqClient):
        self.llm = llm_client
        
    def generate_pulse(self, reviews: list[Review]) -> PulseReport:
        if not reviews:
            raise ValueError("No reviews provided for analysis.")
            
        # 1. Sentiment Bucketing
        buckets = {
            "Detractors (1-2 stars)": [r for r in reviews if r.rating <= 2],
            "Passives (3 stars)": [r for r in reviews if r.rating == 3],
            "Promoters (4-5 stars)": [r for r in reviews if r.rating >= 4],
        }
        
        all_local_themes = []
        
        # 2. Map Phase (Chunking)
        for sentiment, bucket_reviews in buckets.items():
            if not bucket_reviews:
                continue
                
            # Split bucket into chunks of CHUNK_SIZE
            for i in range(0, len(bucket_reviews), self.CHUNK_SIZE):
                chunk = bucket_reviews[i:i + self.CHUNK_SIZE]
                chunk_data = [
                    {"text": r.text, "title": r.title, "rating": r.rating, "source": r.source} 
                    for r in chunk
                ]
                
                prompt = LOCAL_ANALYSIS_PROMPT.format(
                    sentiment_category=sentiment,
                    reviews_json=json.dumps(chunk_data)
                )
                
                # Fetch local themes for this chunk
                try:
                    response_data = self.llm.generate(prompt, expect_json=True)
                    local_themes = response_data.get("local_themes", [])
                    # Append sentiment tag for the synthesis phase
                    for theme in local_themes:
                        theme["_source_sentiment"] = sentiment
                    all_local_themes.extend(local_themes)
                except Exception as e:
                    print(f"Warning: Failed to process chunk for {sentiment}. Error: {e}")
                    
        if not all_local_themes:
            raise ValueError("Failed to extract any local themes during the Map phase.")
            
        # 3. Reduce Phase (Synthesis)
        synth_prompt = SYNTHESIS_PROMPT.format(local_themes_json=json.dumps(all_local_themes))
        
        try:
            final_data = self.llm.generate(synth_prompt, expect_json=True)
            
            themes = [Theme(**t) for t in final_data.get("themes", [])]
            quotes = [Quote(**q) for q in final_data.get("quotes", [])]
            actions = final_data.get("actions", [])
            
            # Enforce constraints
            if len(themes) > 5:
                themes = themes[:5]
                
            return PulseReport(
                generated_date=datetime.now().isoformat(),
                themes=themes,
                quotes=quotes,
                actions=actions
            )
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response during Synthesis phase: {e}")
