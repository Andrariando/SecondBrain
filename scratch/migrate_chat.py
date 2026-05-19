import os
import sys
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

load_dotenv(dotenv_path=os.path.join(parent_dir, '.env'), override=True)

from app.db import SessionLocal
from app.models import Memory, KnowledgeNote

def migrate_chat_history():
    db = SessionLocal()
    try:
        # Any 'knowledge' memory where the source_id does NOT end in .pdf or .txt
        # is a chat history message (source_id is phone number).
        # We will reclassify them to 'chat' and delete their KnowledgeNote sub-record.
        
        memories = db.query(Memory).filter(Memory.type == "knowledge").all()
        count = 0
        for m in memories:
            if m.source_id and not (m.source_id.endswith(".pdf") or m.source_id.endswith(".txt") or m.source_id.endswith(".md")):
                m.type = "chat"
                
                # delete the knowledge note if it exists
                kn = db.query(KnowledgeNote).filter(KnowledgeNote.memory_id == m.id).first()
                if kn:
                    db.delete(kn)
                    
                count += 1
                
        db.commit()
        print(f"Successfully migrated {count} memories from 'knowledge' to 'chat'.")
        
    except Exception as e:
        print(f"Error migrating: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_chat_history()
