from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from backend.api import upload, chat, sessions, documents
from backend.database import engine
from backend import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="VaultRAG API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(os.path.join("data", "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory="data"), name="static")

app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(documents.router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health/detailed")
def detailed_health():
    import subprocess
    import httpx
    from backend.api.chat import last_query_metrics
    from backend.config import LOCAL_LLM_MODEL, EMBEDDING_MODEL, OLLAMA_BASE_URL
    
    vram = None
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            encoding="utf-8"
        )
        vram = int(output.strip())
    except Exception:
        pass

    ollama_status = "unreachable"
    try:
        r = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=1.0)
        if r.status_code == 200:
            ollama_status = "running"
    except Exception:
        pass

    last_query = None
    if last_query_metrics and last_query_metrics.get("query"):
        last_query = {
            "query": last_query_metrics["query"],
            "retrieval_ms": last_query_metrics["retrieval_latency_sec"] * 1000,
            "synthesis_ms": last_query_metrics["synthesis_latency_sec"] * 1000,
            "total_ms": last_query_metrics["total_latency_sec"] * 1000,
        }
         
    return {
        "status": "ok",
        "models": {
            "embedding": EMBEDDING_MODEL,
            "chat": LOCAL_LLM_MODEL,
        },
        "vram_usage_mb": vram,
        "ollama_status": ollama_status,
        "last_query_latency": last_query,
    }
