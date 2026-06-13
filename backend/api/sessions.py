from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
import uuid
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/sessions", tags=["sessions"])

class SessionCreate(BaseModel):
    title: str

class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: str

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    citations: Optional[str] = None
    timestamp: str

@router.get("", response_model=List[SessionResponse])
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(models.ChatSession).order_by(models.ChatSession.created_at.desc()).all()
    return [
        {"id": s.id, "title": s.title, "created_at": s.created_at.isoformat()}
        for s in sessions
    ]

@router.post("", response_model=SessionResponse)
def create_session(session_in: SessionCreate, db: Session = Depends(get_db)):
    new_id = str(uuid.uuid4())
    new_session = models.ChatSession(id=new_id, title=session_in.title)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"id": new_session.id, "title": new_session.title, "created_at": new_session.created_at.isoformat()}

@router.get("/{session_id}/messages", response_model=List[MessageResponse])
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    messages = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).order_by(models.ChatMessage.timestamp).all()
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "citations": m.citations,
            "timestamp": m.timestamp.isoformat()
        }
        for m in messages
    ]

@router.delete("/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    # Delete associated messages first
    db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).delete()
    db.delete(session)
    db.commit()
    return {"message": "Session deleted"}