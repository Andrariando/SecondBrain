import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db import Base

def generate_uuid():
    return str(uuid.uuid4())

class Memory(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, default=generate_uuid)
    type = Column(String, nullable=False) # action_item, idea, knowledge
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String, default='active')
    priority = Column(String, nullable=True)
    source_channel = Column(String, default='whatsapp')
    source_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    memory_id = Column(String, ForeignKey("memories.id", ondelete="CASCADE"))
    deadline = Column(String, nullable=True)
    owner = Column(String, nullable=True)
    next_step = Column(String, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class Idea(Base):
    __tablename__ = "ideas"

    id = Column(String, primary_key=True, default=generate_uuid)
    memory_id = Column(String, ForeignKey("memories.id", ondelete="CASCADE"))
    maturity = Column(String, nullable=True)
    possible_use = Column(String, nullable=True)
    next_step = Column(String, nullable=True)

class KnowledgeNote(Base):
    __tablename__ = "knowledge_notes"

    id = Column(String, primary_key=True, default=generate_uuid)
    memory_id = Column(String, ForeignKey("memories.id", ondelete="CASCADE"))
    course = Column(String, nullable=True)
    topic = Column(String, nullable=True)
    source_doc = Column(String, nullable=True)
    confidence = Column(String, nullable=True)
