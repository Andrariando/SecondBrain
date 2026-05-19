from app.openai_client import call_llm_json

SYSTEM_PROMPT = """
You extract structured memory from personal notes.
Return strict JSON only.
Do not invent missing details.
Use null when information is missing.
"""

def extract_memory(message: str, memory_type: str) -> dict:
    if memory_type == "action_item":
        format_instructions = """
        {
          "title": "short title",
          "description": "longer description",
          "deadline": "extracted deadline or null",
          "priority": "high/medium/low or null",
          "owner": "who is doing it or null",
          "next_step": "immediate next action or null"
        }
        """
    elif memory_type == "idea":
        format_instructions = """
        {
          "title": "short title",
          "summary": "longer summary",
          "maturity": "rough/developing/mature",
          "possible_use": "what this could be used for or null",
          "next_step": "how to develop this idea or null"
        }
        """
    elif memory_type == "knowledge":
        format_instructions = """
        {
          "title": "short title",
          "summary": "longer summary",
          "course": "course name if mentioned or null",
          "topic": "main topic",
          "confidence": "high/medium/low",
          "source_doc": "mentioned paper or book or null"
        }
        """
    else:
        format_instructions = """
        {
          "title": "short title",
          "summary": "summary of the request"
        }
        """

    user_prompt = f"""
Extract fields for a {memory_type} from this message:

{message}

Return JSON with exactly this format:
{format_instructions}
"""
    return call_llm_json(SYSTEM_PROMPT, user_prompt)
