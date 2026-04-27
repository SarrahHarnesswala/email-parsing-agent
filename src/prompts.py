"""
Prompt templates for the email parsing agent.

These prompts guide the LLM on how to extract and structure information
from emails. We use specific formatting instructions to ensure consistent
JSON output that we can reliably parse.
"""

EMAIL_PARSING_PROMPT = """You are an email analysis expert. Your task is to extract and categorize information from emails.

Analyze the following email and extract the requested information. Return ONLY a valid JSON object with no additional text.

Email:
{email_text}

Extract the following fields:
1. sender: The email address or name of the sender
2. subject: The email subject line
3. date: The date the email was sent (if available)
4. main_intent: A brief (1-2 sentence) summary of the primary purpose of the email
5. action_items: A list of specific tasks or actions requested (if any). Return as an array of strings.
6. urgency_level: Classify as "high", "medium", or "low" based on language cues, keywords, and context

Return the response as valid JSON only, with no markdown code blocks or additional text:
{{
    "sender": "...",
    "subject": "...",
    "date": "...",
    "main_intent": "...",
    "action_items": [...],
    "urgency_level": "..."
}}"""
