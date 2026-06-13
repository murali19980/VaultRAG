from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    from backend.api.chat import last_query_metrics
    from backend.config import LOCAL_LLM_MODEL, EMBEDDING_MODEL, USE_LOCAL_LLM
    
    vram = None
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            encoding="utf-8"
        )
        vram = f"{output.strip()} MiB"
    except Exception:
        pass
         
    return {
        "status": "ok",
        "configuration": {
            "use_local_llm": USE_LOCAL_LLM,
            "llm_model": LOCAL_LLM_MODEL,
            "embedding_model": EMBEDDING_MODEL,
        },
        "system_resources": {
            "gpu_vram_used": vram,
        },
        "last_query_metrics": last_query_metrics,
    }
