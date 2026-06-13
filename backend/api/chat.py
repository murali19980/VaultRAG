import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.ingestion.embeddings import get_embedding_model
from backend.models import ChatMessage, ChatSession
from backend.qa.citation_extractor import extract_citations
from backend.qa.query_engine import get_query_engine
from backend.retrieval.bm25_index import BM25Index
from backend.retrieval.hybrid_retriever import HybridRetriever
from backend.retrieval.vector_store import get_chroma_vector_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    citations: List[Dict[str, Any]]


_query_engine = None

last_query_metrics = {
    "query": None,
    "retrieval_latency_sec": 0.0,
    "synthesis_latency_sec": 0.0,
    "total_latency_sec": 0.0,
    "timestamp": None,
}


def _get_or_create_query_engine():
    global _query_engine
    if _query_engine is None:
        logger.info("Initialising query engine for first use")
        vector_store = get_chroma_vector_store()
        bm25 = BM25Index()
        embed_model = get_embedding_model()
        retriever = HybridRetriever(
            vector_store=vector_store,
            bm25_index=bm25,
            embed_model=embed_model,
        )
        _query_engine = get_query_engine(retriever)
    return _query_engine


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    sid = request.session_id or str(uuid.uuid4())

    existing = db.query(ChatSession).filter(ChatSession.id == sid).first()
    if not existing:
        session = ChatSession(id=sid, title=request.message[:80])
        db.add(session)
        db.commit()

    user_msg = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=sid,
        role="user",
        content=request.message,
    )
    db.add(user_msg)
    db.commit()

    import time
    from datetime import datetime

    try:
        engine = _get_or_create_query_engine()
        t0 = time.time()
        nodes = engine.retriever.retrieve(request.message)
        t_retrieval = time.time() - t0
        
        t1 = time.time()
        response = engine._response_synthesizer.synthesize(request.message, nodes)
        t_synthesis = time.time() - t1
        
        t_total = time.time() - t0
        
        last_query_metrics["query"] = request.message
        last_query_metrics["retrieval_latency_sec"] = t_retrieval
        last_query_metrics["synthesis_latency_sec"] = t_synthesis
        last_query_metrics["total_latency_sec"] = t_total
        last_query_metrics["timestamp"] = datetime.utcnow().isoformat()
    except Exception as e:
        logger.exception("Query engine call failed")
        raise HTTPException(status_code=500, detail=f"Failed to generate answer. Error: {str(e)}")

    citations = extract_citations(response)
    citations_json = json.dumps(citations, default=str)

    assistant_msg = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=sid,
        role="assistant",
        content=str(response),
        citations=citations_json,
    )
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(
        session_id=sid,
        answer=str(response),
        citations=citations,
    )
