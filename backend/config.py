import os
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/vaultrag")
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "llama3.2:3b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# New constant – used in both ingestion and retrieval
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "vaultrag")

