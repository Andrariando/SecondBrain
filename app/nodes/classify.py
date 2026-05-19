from app.openai_client import call_llm_json

SYSTEM_PROMPT = """
You classify personal second-brain inputs.
Return strict JSON only.
Allowed categories:
- action_item
- idea
- knowledge
- research_request
- question
"""

def classify_message(message: str) -> dict:
    user_prompt = f"""
Classify this message:

{message}

Return JSON with exactly this format:
{{
    "type": "<one of the allowed categories>",
    "confidence": "<high|medium|low>",
    "reasoning_summary": "<brief explanation>"
}}
"""
    return call_llm_json(SYSTEM_PROMPT, user_prompt)
