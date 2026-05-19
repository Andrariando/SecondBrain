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

@router.get("/memories/{memory_id}/related")
def get_related_memories(memory_id: str, db: Session = Depends(get_db)):
    """Find semantically related knowledge articles."""
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory or memory.type != 'knowledge':
        return {"related": []}
        
    try:
        from app.vector_db import get_knowledge_collection
        collection = get_knowledge_collection()
        
        # Query ChromaDB with the first 1000 chars of this document
        results = collection.query(
            query_texts=[memory.content[:1000]],
            n_results=10
        )
        
        related_sources = set()
        if results and "metadatas" in results and results["metadatas"]:
            for meta in results["metadatas"][0]:
                if meta and "source" in meta:
                    src = meta["source"]
                    if src != memory.source_id:
                        related_sources.add(src)
                        
        if not related_sources:
            return {"related": []}
            
        # Fetch actual memory items for those sources
        related_memories = db.query(Memory)\
            .filter(Memory.source_id.in_(list(related_sources)))\
            .filter(Memory.id != memory_id)\
            .filter(Memory.type == 'knowledge')\
            .limit(3)\
            .all()
            
        result = [{"id": rm.id, "title": rm.title} for rm in related_memories]
        return {"related": result}
        
    except Exception as e:
        print(f"Error fetching related memories: {e}")
        return {"related": []}
