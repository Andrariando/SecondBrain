import os
import pypdf
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Memory, KnowledgeNote
from app.openai_client import call_llm_json

router = APIRouter()

def process_document(file_path: str, filename: str, db: Session):
    text = ""
    if filename.endswith(".pdf"):
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    elif filename.endswith(".txt") or filename.endswith(".md"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        print(f"Unsupported file type: {filename}")
        return

    prompt = """
    You are an AI assistant analyzing a document for a personal knowledge wiki.
    Your goal is to write a highly detailed, comprehensive, exhaustive Wikipedia-style article based on the document.
    
    IMPORTANT: The 'summary' field MUST be extremely detailed (at least 500-1000 words).
    Do NOT return a short block of text. Use markdown headers (e.g. ## Overview, ## Deep Dive, ## Key Concepts, ## Action Items), bullet points (-), and bold text (**) to make it readable.
    Extract every important detail, concept, and takeaway.
    
    Return JSON format:
    {
        "title": "Document Title",
        "topic": "Main Topic",
        "summary": "## Overview\n...\n## Key Insights\n- ...",
        "confidence": "high"
    }
    """
    try:
        # truncate text if it's too long
        safe_text = text[:40000] 
        result = call_llm_json(prompt, f"Document Name: {filename}\n\nContent:\n{safe_text}")
        
        memory = Memory(
            type="knowledge",
            title=result.get("title", filename),
            content=result.get("summary", "Extracted document content"),
            source_channel="wiki_upload",
            source_id=filename
        )
        db.add(memory)
        db.flush()
        
        kn = KnowledgeNote(
            memory_id=memory.id,
            topic=result.get("topic", "General"),
            source_doc=filename,
            confidence=result.get("confidence", "high")
        )
        db.add(kn)
        db.commit()
        print(f"Successfully processed {filename}")
        
        # Step 2: Embed into Vector Database (ChromaDB) for RAG
        from app.vector_db import get_knowledge_collection
        
        def chunk_text(t, chunk_size=1000, overlap=200):
            chunks = []
            start = 0
            while start < len(t):
                end = start + chunk_size
                chunks.append(t[start:end])
                start += (chunk_size - overlap)
            return chunks
            
        chunks = chunk_text(text)
        if chunks:
            collection = get_knowledge_collection()
            ids = [f"{filename}_{i}" for i in range(len(chunks))]
            metadatas = [{"source": filename, "title": result.get("title", filename)} for _ in chunks]
            
            collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Embedded {len(chunks)} chunks into ChromaDB for {filename}")
            
    except Exception as e:
        print(f"Error processing document {filename}: {e}")
        db.rollback()

@router.post("")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    upload_dir = os.path.join(os.getcwd(), "storage", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    background_tasks.add_task(process_document, file_path, file.filename, db)
    
    return {"status": "success", "message": f"File '{file.filename}' uploaded and is being processed by the AI in the background."}
