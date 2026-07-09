import time
from groq import Groq

class GroqClient:
    """Wrapper for the Groq API to draft the final prose report."""
    
    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model_name
        
    def generate_draft(self, prompt: str, max_retries: int = 3) -> str:
        """
        Send a prompt to Groq and return the markdown text response.
        """
        for attempt in range(max_retries):
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=self.model,
                    temperature=0.3, # Low temperature for professional consistency
                )
                return chat_completion.choices[0].message.content
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Groq generation failed after {max_retries} attempts: {e}")
                time.sleep(2 ** attempt) # Exponential backoff
