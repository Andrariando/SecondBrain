import os
import json
from openai import OpenAI
import anthropic

openai_client = OpenAI()
anthropic_client = anthropic.Anthropic()

def call_llm_json(system_prompt: str, user_prompt: str, provider: str = "openai", model: str = "gpt-4o-mini") -> dict:
    """
    Calls either OpenAI or Anthropic to extract JSON.
    """
    if provider == "openai":
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    
    elif provider == "anthropic":
        # If user asks for anthropic but passes an OpenAI model name, translate it
        if "gpt" in model:
            model = "claude-3-haiku-20240307"
            
        full_system = system_prompt + "\n\nYou MUST return ONLY valid JSON and no other text."
        response = anthropic_client.messages.create(
            model=model,
            max_tokens=1024,
            system=full_system,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        content = response.content[0].text
        # Strip markdown if Claude adds it
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    
    raise ValueError(f"Unknown provider: {provider}")
