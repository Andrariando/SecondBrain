import sys
import os

# Add the parent directory to sys.path so we can import 'app'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app.db import engine, Base
# Import all models so SQLAlchemy registers them before create_all()
from app.models import Memory, ActionItem, Idea, KnowledgeNote

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database initialized successfully!")
