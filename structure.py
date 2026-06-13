#!/usr/bin/env python3
"""
VaultRAG Project Structure Generator
Run this script to create the complete folder and file layout for VaultRAG.
"""

import os
import stat

# Base path
BASE_DIR = r"E:\VaultRAG"

# Define the complete structure as nested dict: {filename_or_dir: content_or_children}
# For directories, value is a dict of children.
# For files, value is a string (content) or None to create an empty file.

STRUCTURE = {
    "README.md": """# VaultRAG – Air-Gapped Enterprise Knowledge Base

A completely local, secure web app where a company can upload private PDFs, HR documents, and financial reports.
Users can chat with the documents, and the AI provides answers with exact page‑number citations.

## Features
- Hybrid Search (Vector + BM25) with Reciprocal Rank Fusion (RRF)
- Contextual Chunking (preserves tables, code blocks)
- Citations with page numbers and source files
- Air‑gap ready – can run fully offline with Ollama

## Tech Stack
- **Backend**: FastAPI, LlamaIndex, ChromaDB, Whoosh (BM25)
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Database**: PostgreSQL (chat history)
- **Embeddings**: nomic-embed-text via Ollama
- **LLM**: OpenRouter free tier (or local Ollama for air‑gap)

## Setup
1. Install Python 3.10+, Node.js 22+, Docker (optional), Ollama
2. Pull embedding model: `ollama pull nomic-embed-text`
3. Run PostgreSQL (or use Docker: `docker-compose up -d`)
4. Backend: `pip install -r requirements.txt && uvicorn backend.main:app --reload`
5. Frontend: `cd frontend && npm install && npm run dev`
6. Open http://localhost:3000

## Environment Variables
Copy `.env.example` to `.env` and fill in:
- `OPENROUTER_API_KEY` (if using cloud LLM)
- `DATABASE_URL` (PostgreSQL connection string)
""",
    ".env.example": """# Backend
OPENROUTER_API_KEY=your_key_here
OLLAMA_BASE_URL=http://localhost:11434

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/vaultrag

# Optional: Use local LLM instead of OpenRouter (set to true)
USE_LOCAL_LLM=false
LOCAL_LLM_MODEL=llama3.2:3b
""",
    ".gitignore": """# Python
__pycache__/
*.pyc
venv/
.env
data/
chroma_db/
bm25_index/
uploads/

# Node
node_modules/
.next/
out/
dist/

# IDE
.vscode/
.idea/

# Logs
*.log
""",
    "docker-compose.yml": """version: '3.8'
services:
  postgres:
    image: postgres:15
    container_name: vaultrag_postgres
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: vaultrag
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
""",
    "requirements.txt": """fastapi==0.115.0
uvicorn[standard]==0.30.0
python-multipart==0.0.12
sqlalchemy==2.0.35
psycopg2-binary==2.9.10
llama-index==0.10.55
llama-index-vector-stores-chroma==0.1.19
llama-index-llms-openrouter==0.1.9
llama-index-llms-ollama==0.2.1
chromadb==0.4.24
whoosh==2.7.4
pypdf2==3.0.1
pandas==2.2.2
openpyxl==3.1.2
ollama==0.3.0
scikit-learn==1.5.1
""",
    "requirements-dev.txt": """pytest==8.3.0
black==24.4.0
mypy==1.10.0
""",
    "setup.sh": """#!/bin/bash
# Setup script for VaultRAG (Linux/macOS/WSL)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ollama pull nomic-embed-text
echo "Setup complete. Run 'docker-compose up -d' for PostgreSQL."
""",
    "backend": {
        "__init__.py": "",
        "main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import upload, chat, sessions, documents
from backend.database import engine
from backend import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="VaultRAG API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"])

app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(documents.router)

@app.get("/health")
def health():
    return {"status": "ok"}
""",
        "config.py": """import os
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/vaultrag")
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "llama3.2:3b")
""",
        "models.py": """from sqlalchemy import Column, String, Text, DateTime
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
""",
        "database.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
        "ingestion": {
            "__init__.py": "",
            "loader.py": "# Load PDF, Excel, Word files using LlamaIndex SimpleDirectoryReader",
            "chunker.py": "# Contextual chunking: hierarchical parser + table/code block preservation",
            "embeddings.py": "# OllamaEmbedding wrapper for nomic-embed-text",
            "indexer.py": "# Orchestrate loading -> chunking -> embedding -> store in Chroma + BM25",
        },
        "retrieval": {
            "__init__.py": "",
            "vector_store.py": "# ChromaDB persistent client wrapper",
            "bm25_index.py": "# Whoosh BM25 index builder and searcher",
            "hybrid_retriever.py": "# HybridRetriever with Reciprocal Rank Fusion (RRF)",
            "reranker.py": "# Optional cross-encoder reranker (stub)",
        },
        "qa": {
            "__init__.py": "",
            "query_engine.py": "# LlamaIndex RetrieverQueryEngine wrapper",
            "prompt_templates.py": "# Custom prompts for answer generation",
            "citation_extractor.py": "# Extract page numbers, filenames, and snippets from source nodes",
        },
        "api": {
            "__init__.py": "",
            "upload.py": "# POST /upload endpoint",
            "chat.py": "# POST /chat endpoint",
            "sessions.py": "# GET /sessions, DELETE /sessions/{id}",
            "documents.py": "# GET /documents, DELETE /documents",
        },
        "utils": {
            "__init__.py": "",
            "file_utils.py": "# Temporary file handling, allowed extensions",
            "logging_config.py": "# Structured logging setup",
            "validation.py": "# Input sanitisation, size limits",
        },
    },
    "frontend": {
        "package.json": """{
  "name": "vaultrag-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.2.5",
    "react": "^18",
    "react-dom": "^18",
    "axios": "^1.7.2",
    "lucide-react": "^0.394.0",
    "tailwindcss": "^3.4.1"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "typescript": "^5"
  }
}
""",
        "tsconfig.json": """{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
""",
        "tailwind.config.js": """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: { extend: {} },
  plugins: [],
}
""",
        "postcss.config.js": "module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } }",
        "next.config.js": "/** @type {import('next').NextConfig} */\nconst nextConfig = { output: 'standalone' };\nmodule.exports = nextConfig;",
        "public": {
            "favicon.ico": "",
            "logo.svg": "",
        },
        "src": {
            "app": {
                "layout.tsx": """import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = { title: 'VaultRAG', description: 'Air‑gapped Enterprise KB' };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
""",
                "page.tsx": "// Main chat interface – see previous code example",
                "globals.css": "@tailwind base; @tailwind components; @tailwind utilities;",
                "sessions": {
                    "page.tsx": "// List and manage chat sessions",
                },
                "api": {
                    "proxy": {
                        "[...path]": {
                            "route.ts": "// Optional proxy to FastAPI to avoid CORS",
                        },
                    },
                },
            },
            "components": {
                "ChatInput.tsx": "// Textarea + send button",
                "ChatMessage.tsx": "// Renders user/assistant bubble with citations",
                "CitationBadge.tsx": "// Inline citation pill",
                "FileUploader.tsx": "// Drag‑and‑drop PDF upload",
                "SessionSidebar.tsx": "// Left sidebar with session history",
                "TypingIndicator.tsx": "// Animated dots while LLM generates",
            },
            "hooks": {
                "useChat.ts": "// Manage messages, send requests",
                "useSessions.ts": "// Fetch/create/delete sessions",
                "useUpload.ts": "// File upload state",
            },
            "lib": {
                "api.ts": "// Axios instance",
                "types.ts": "// TypeScript interfaces",
            },
            "styles": {
                "markdown.css": "// Styling for LLM markdown responses",
            },
        },
    },
    "data": {},
    "scripts": {
        "reset_db.py": "#!/usr/bin/env python3\n# Drop and recreate PostgreSQL tables",
        "clear_indexes.py": "#!/usr/bin/env python3\n# Delete Chroma and BM25 indexes",
        "test_ingest.py": "#!/usr/bin/env python3\n# Ingest sample PDF and verify chunks",
    },
    "tests": {
        "test_ingestion.py": "# Unit tests for chunker, embeddings",
        "test_retrieval.py": "# Test hybrid retriever",
        "test_api.py": "# FastAPI endpoint tests",
    },
}

def create_structure(base_path, struct):
    for name, content in struct.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            parent = os.path.dirname(path)
            if parent and not os.path.exists(parent):
                os.makedirs(parent, exist_ok=True)
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Created: {path}")
            else:
                print(f"Skipped (exists): {path}")

if __name__ == "__main__":
    print(f"Creating VaultRAG structure under {BASE_DIR}")
    create_structure(BASE_DIR, STRUCTURE)
    print("\nDone! You can now populate the placeholder files with actual implementation.")
    print("See the provided code examples for ingestion, hybrid retriever, and API.")
