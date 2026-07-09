"""
Prompt templates for Groq Final Drafting.
"""

DRAFTING_PROMPT = """
You are an expert product communicator. I am providing you with a structured "Weekly Pulse Report" containing raw themes, quotes, and actionable steps extracted from user reviews.

Your task is to transform this structured data into a highly readable, professional, and scannable executive summary.

Here is the structured JSON report:
{report_json}

Requirements:
1. Tone: Professional, concise, and scannable.
2. Length: Under 250 words total.
3. Structure: 
   - A brief introductory sentence.
   - Bullet points for the top themes (max 3), integrating the quotes seamlessly (e.g. "Users noted X, with one stating 'quote text'").
   - A "Next Steps" section summarizing the actions.
4. EXACT MARKER REQUIRED: You MUST include the exact text `{{doc_url}}` at the very end of the report (e.g. "Full detailed report: {{doc_url}}"). Do not format it as [Link text]({{doc_url}}).

Output ONLY the final markdown text.
"""
