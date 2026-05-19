import os
import chromadb
from chromadb.utils import embedding_functions

# Get the directory where we want to store the ChromaDB SQLite file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
chroma_path = os.path.join(parent_dir, "storage", "chroma")
os.makedirs(chroma_path, exist_ok=True)

# Initialize Chroma persistent client
chroma_client = chromadb.PersistentClient(path=chroma_path)

# Initialize OpenAI embedding function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

# Get or create the knowledge collection
def get_knowledge_collection():
    return chroma_client.get_or_create_collection(
        name="knowledge",
        embedding_function=openai_ef
    )
