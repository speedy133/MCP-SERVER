"""
Prompt templates for the LLM processing engine (Map-Reduce Architecture).
"""

LOCAL_ANALYSIS_PROMPT = """
You are a product analyst. I am providing you with a batch of user reviews belonging to the following sentiment category: {sentiment_category}.

Here are the reviews (in JSON format):
{reviews_json}

Your task is to extract local themes from this specific batch.
Identify the recurring themes (up to 3). For each theme, provide the name, a short description, and exactly one verbatim quote from the provided reviews that illustrates it.

Respond ONLY with a valid JSON object matching this schema:
{{
  "local_themes": [
    {{
      "name": "Theme name",
      "description": "Short description",
      "quote_text": "Exact verbatim text from a review in this batch",
      "source": "play_store|app_store",
      "rating": 5
    }}
  ]
}}
"""

SYNTHESIS_PROMPT = """
You are a Lead Product Analyst. Your team has processed thousands of reviews and extracted the following local themes and quotes across different sentiment buckets.

Here are all the local themes:
{local_themes_json}

Your task is to synthesize these into a final "Weekly Pulse Report".

Requirements:
1. Deduplicate and merge the local themes into a final list of the Top 5 Global Themes. Rank them by priority (1 being highest).
2. For the top 3 global themes, pick the single best quote from the provided local themes. The quote MUST be exact.
3. Recommend exactly 3 actionable next steps for the product/engineering team based on the most critical themes (usually the detractors).

Respond ONLY with a valid JSON object matching this schema:
{{
  "themes": [
    {{
      "name": "Short global theme name",
      "description": "1 sentence describing the theme",
      "priority": 1,
      "sentiment": "positive|neutral|negative"
    }}
  ],
  "quotes": [
    {{
      "theme_name": "Short global theme name",
      "quote_text": "Exact text from the provided quotes",
      "source": "play_store|app_store",
      "rating": 5
    }}
  ],
  "actions": [
    "Actionable step 1",
    "Actionable step 2",
    "Actionable step 3"
  ]
}}
"""
