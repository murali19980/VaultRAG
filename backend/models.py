from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    title = Column(String)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String)
    content = Column(Text)
    citations = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
