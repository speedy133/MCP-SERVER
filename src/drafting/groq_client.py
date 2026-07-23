import time
from groq import Groq

class GroqClient:
    """Wrapper for the Groq API to draft the final prose report."""
    
    def __init__(self, api_key: str, model_name: str = "llama-3.1-8b-instant"):
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

    def generate(self, prompt: str, expect_json: bool = True, max_retries: int = 3) -> dict | str:
        """
        Send a prompt to Groq and return the response.
        If expect_json is True, the response is parsed into a Python dict.
        """
        import json
        # We enforce a json type hint in the prompt if we expect JSON
        json_prompt = prompt
        if expect_json:
            json_prompt += "\n\nYou must output ONLY valid JSON format."

        raw_response = self.generate_draft(json_prompt, max_retries)
        
        if expect_json:
            try:
                # Often LLMs wrap JSON in markdown blocks
                clean_text = raw_response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                return json.loads(clean_text)
            except json.JSONDecodeError as e:
                print(f"Failed to parse Groq response as JSON. Raw response:\n{raw_response}")
                raise e
                
        return raw_response

