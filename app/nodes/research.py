from app.openai_client import call_llm_json
from app.vector_db import get_knowledge_collection
from duckduckgo_search import DDGS

SYSTEM_PROMPT = """
You are a brilliant research assistant acting as a second brain for the user.
The user has asked a question or requested a briefing on a topic.
You have been provided with context from the user's personal Wiki (uploaded documents) AND context from the live Internet.

INSTRUCTIONS:
1. Use the provided context to accurately answer their question. 
2. If the user explicitly asks for a "briefing" or "report", use a highly structured markdown format (Executive Summary, Key Concepts, Takeaways).
3. Otherwise, answer naturally and conversationally like a human expert. Use markdown (bold, lists) only if it helps readability. Do NOT force rigid corporate headers for simple questions.

Return strict JSON only.
"""

def generate_research_briefing(message: str) -> dict:
    format_instructions = """
    {
      "title": "A short, descriptive title for the response",
      "briefing": "Your naturally formatted markdown response (can be conversational or a strict briefing, depending on the request)"
    }
    """
    
    # 1. Retrieve relevant context from ChromaDB (Personal Wiki)
    wiki_context = "No relevant context found in Wiki."
    try:
        collection = get_knowledge_collection()
        results = collection.query(
            query_texts=[message],
            n_results=5
        )
        
        if results and results["documents"] and len(results["documents"][0]) > 0:
            context_chunks = results["documents"][0]
            sources = [meta.get("source", "Unknown") for meta in results["metadatas"][0]]
            
            context_parts = []
            for i, chunk in enumerate(context_chunks):
                context_parts.append(f"Source: {sources[i]}\nContent:\n{chunk}")
            wiki_context = "\n\n---\n\n".join(context_parts)
    except Exception as e:
        print(f"Error querying ChromaDB: {e}")
        
    # 2. Retrieve relevant context from the live internet (DuckDuckGo)
    web_context = "No relevant web context found."
    try:
        with DDGS() as ddgs:
            # Get top 3 search results
            results = list(ddgs.text(message, max_results=3))
            if results:
                web_parts = []
                for r in results:
                    web_parts.append(f"Source: {r.get('href')}\nSnippet: {r.get('body')}")
                web_context = "\n\n---\n\n".join(web_parts)
    except Exception as e:
        print(f"Error querying DuckDuckGo: {e}")
    
    user_prompt = f"""
User's message: {message}

=== CONTEXT FROM USER'S WIKI ===
{wiki_context}
================================

=== CONTEXT FROM LIVE INTERNET ===
{web_context}
==================================

Return JSON with exactly this format:
{format_instructions}
"""
    return call_llm_json(SYSTEM_PROMPT, user_prompt)
