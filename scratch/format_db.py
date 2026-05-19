import os
import sys
import pypdf
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

load_dotenv(dotenv_path=os.path.join(parent_dir, '.env'), override=True)

from app.db import SessionLocal
from app.models import Memory
from app.openai_client import call_llm_json

def reprocess_pdf():
    db = SessionLocal()
    try:
        memory = db.query(Memory).filter(Memory.title.like('%AWS_Interview_Master_Guide%')).first()
        if not memory:
            print("Memory not found.")
            return

        print(f"Found memory: {memory.title}")
        
        pdf_path = os.path.join(parent_dir, "storage", "uploads", "Diandra_AWS_Interview_Master_Guide_1.pdf")
        
        text = ""
        with open(pdf_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
                
        safe_text = text[:40000]
        
        prompt = f"""
        You are an AI assistant analyzing an AWS Interview Guide for a personal knowledge wiki.
        Your goal is to write a highly detailed, comprehensive, exhaustive Wikipedia-style article based on the document.
        
        IMPORTANT: The 'markdown' field MUST be extremely detailed (at least 500-800 words).
        Do NOT return a short block of text. Use markdown headers (e.g. ## Overview, ## Leadership Principles, ## STAR Stories, ## Deep Dive), bullet points (-), and bold text (**) to make it readable.
        Extract every important detail, concept, and takeaway from the document.
        
        Return JSON format:
        {{
            "markdown": "Your massive, detailed markdown string goes here"
        }}
        """
        
        result = call_llm_json(prompt, f"Document Content:\n{safe_text}")
        
        memory.content = result.get("markdown", memory.content)
        db.commit()
        print("Successfully reprocessed the PDF and saved a massive Markdown summary.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reprocess_pdf()
