import os
import sys
import pypdf
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

load_dotenv(dotenv_path=os.path.join(parent_dir, '.env'), override=True)

from app.vector_db import get_knowledge_collection

def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def embed_existing_pdf():
    try:
        pdf_path = os.path.join(parent_dir, "storage", "uploads", "Diandra_AWS_Interview_Master_Guide_1.pdf")
        if not os.path.exists(pdf_path):
            print(f"File not found: {pdf_path}")
            return
            
        print("Extracting text...")
        text = ""
        with open(pdf_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
                
        print("Chunking text...")
        chunks = chunk_text(text)
        
        print("Embedding into ChromaDB...")
        collection = get_knowledge_collection()
        
        filename = "Diandra_AWS_Interview_Master_Guide_1.pdf"
        title = "AWS Interview Master Guide"
        
        ids = [f"{filename}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "title": title} for _ in chunks]
        
        collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Successfully embedded {len(chunks)} chunks into ChromaDB.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    embed_existing_pdf()
