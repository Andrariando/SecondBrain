from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Memory, ActionItem, Idea, KnowledgeNote

router = APIRouter()

@router.get("/memories")
def get_memories(type: str = None, db: Session = Depends(get_db)):
    query = db.query(Memory)
    if type:
        query = query.filter(Memory.type == type)
    
    memories = query.order_by(Memory.created_at.desc()).all()
    
    result = []
    for m in memories:
        data = {
            "id": m.id,
            "type": m.type,
            "title": m.title,
            "content": m.content,
            "status": m.status,
            "source_doc": m.source_id,
            "created_at": m.created_at.isoformat() if m.created_at else None
        }
        result.append(data)
        
    return {"memories": result}

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Memory).count()
    ideas = db.query(Memory).filter(Memory.type == "idea").count()
    actions = db.query(Memory).filter(Memory.type == "action_item").count()
    knowledge = db.query(Memory).filter(Memory.type == "knowledge").count()
    chat = db.query(Memory).filter(Memory.type == "chat").count()
    
    return {
        "total": total,
        "ideas": ideas,
        "actions": actions,
        "knowledge": knowledge,
        "chat": chat
    }
