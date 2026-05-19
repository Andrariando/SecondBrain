import os
import io
import contextlib
import requests
import re
import math
import statistics
import json
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from ddgs import DDGS
from app.vector_db import get_knowledge_collection
from app.db import SessionLocal
from app.models import Memory, ActionItem, Idea

@tool
def search_wiki(query: str) -> str:
    """Searches the user's personal Wiki (ChromaDB) for information from uploaded PDFs and documents. Use this when the user asks about something they uploaded or previously learned."""
    try:
        collection = get_knowledge_collection()
        results = collection.query(query_texts=[query], n_results=5)
        if results and results["documents"] and len(results["documents"][0]) > 0:
            context_chunks = results["documents"][0]
            sources = [meta.get("source", "Unknown") for meta in results["metadatas"][0]]
            
            context_parts = []
            for i, chunk in enumerate(context_chunks):
                context_parts.append(f"Source: {sources[i]}\nContent:\n{chunk}")
            return "\n\n---\n\n".join(context_parts)
        return "No relevant context found in Wiki."
    except Exception as e:
        return f"Error querying Wiki: {e}"

@tool
def search_web(query: str) -> str:
    """Searches the live internet (DuckDuckGo) for real-world data, breaking news, or current events."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                web_parts = []
                for r in results:
                    web_parts.append(f"Source: {r.get('href')}\nSnippet: {r.get('body')}")
                return "\n\n---\n\n".join(web_parts)
        return "No relevant web context found."
    except Exception as e:
        return f"Error querying DuckDuckGo: {e}"

@tool
def save_action_item(phone_number: str, title: str, deadline: str, next_step: str) -> str:
    """Saves an action item or task to the user's database. Call this when the user needs to do something, asks you to remind them, or sets a task."""
    db = SessionLocal()
    try:
        memory = Memory(type="action_item", title=title, content=f"Deadline: {deadline}\nNext Step: {next_step}", source_id=phone_number)
        db.add(memory)
        db.flush()
        item = ActionItem(memory_id=memory.id, deadline=deadline, next_step=next_step)
        db.add(item)
        db.commit()
        return f"Successfully saved action item: {title}"
    except Exception as e:
        db.rollback()
        return f"Error saving action item: {e}"
    finally:
        db.close()

@tool
def save_idea(phone_number: str, title: str, maturity: str, possible_use: str) -> str:
    """Saves an idea to the user's database. Call this when the user has a shower thought, a business idea, or something creative they want to remember."""
    db = SessionLocal()
    try:
        memory = Memory(type="idea", title=title, content=f"Maturity: {maturity}\nPossible Use: {possible_use}", source_id=phone_number)
        db.add(memory)
        db.flush()
        item = Idea(memory_id=memory.id, maturity=maturity, possible_use=possible_use)
        db.add(item)
        db.commit()
        return f"Successfully saved idea: {title}"
    except Exception as e:
        db.rollback()
        return f"Error saving idea: {e}"
    finally:
        db.close()

@tool
def save_note(phone_number: str, title: str, content: str) -> str:
    """Saves a general note or chat context to the user's database."""
    db = SessionLocal()
    try:
        memory = Memory(type="chat", title=title, content=content, source_id=phone_number)
        db.add(memory)
        db.commit()
        return f"Successfully saved note: {title}"
    except Exception as e:
        db.rollback()
        return f"Error saving note: {e}"
    finally:
        db.close()

@tool
def scrape_website(url: str) -> str:
    """Downloads a webpage and extracts its text. Use this when you find a URL that contains information you need to read fully."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator="\n")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        # Limit to first 5000 characters to prevent massive context bloat
        return text[:5000]
    except Exception as e:
        return f"Error scraping {url}: {e}"

@tool
def get_pending_tasks(phone_number: str) -> str:
    """Retrieves all pending action items and tasks for the user from the database."""
    db = SessionLocal()
    try:
        items = db.query(ActionItem, Memory).join(Memory, ActionItem.memory_id == Memory.id).filter(Memory.source_id == phone_number).all()
        if not items:
            return "No pending action items found."
        
        result = "Pending Action Items:\n"
        for act, mem in items:
            result += f"- {mem.title} (Deadline: {act.deadline})\n  Next step: {act.next_step}\n"
        return result
    except Exception as e:
        return f"Error retrieving tasks: {e}"
    finally:
        db.close()

@tool
def search_ideas(phone_number: str, keyword: str) -> str:
    """Searches the user's saved ideas for a specific keyword."""
    db = SessionLocal()
    try:
        items = db.query(Idea, Memory).join(Memory, Idea.memory_id == Memory.id)\
                  .filter(Memory.source_id == phone_number)\
                  .filter((Memory.title.ilike(f"%{keyword}%")) | (Memory.content.ilike(f"%{keyword}%"))).all()
        
        if not items:
            return f"No ideas found matching '{keyword}'."
            
        result = f"Ideas matching '{keyword}':\n"
        for idea, mem in items:
            result += f"- {mem.title} (Maturity: {idea.maturity})\n  Possible use: {idea.possible_use}\n"
        return result
    except Exception as e:
        return f"Error searching ideas: {e}"
    finally:
        db.close()

@tool
def run_python(code: str) -> str:
    """Executes Python code and returns the stdout output. Use this for math, financial calculations, or data analysis. ALWAYS print() your results."""
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code, {})
        return output.getvalue()
    except Exception as e:
        return f"Error executing python code: {e}"
