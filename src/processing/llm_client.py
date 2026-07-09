import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
import time
import json

class LLMClient:
    """Wrapper for the Gemini LLM API with basic retry logic and JSON response support."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
    def generate(self, prompt: str, expect_json: bool = True, max_retries: int = 3) -> dict | str:
        """
        Send a prompt to the LLM and return the response.
        If expect_json is True, the response is parsed into a Python dict.
        """
        # If we expect JSON, give the model a strong hint in generation config
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json" if expect_json else "text/plain"
        )
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt, 
                    generation_config=generation_config
                )
                
                text = response.text
                if expect_json:
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError as e:
                        # Fallback parsing in case the LLM wrapped it in markdown blocks
                        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                        return json.loads(text)
                return text
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"LLM generation failed after {max_retries} attempts: {e}")
                time.sleep(2 ** attempt) # Exponential backoff
