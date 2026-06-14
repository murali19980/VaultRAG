# 🔒 VaultRAG – Local-First Hybrid RAG with Full Document Management

**VaultRAG** is an air‑gapped, privacy‑first Retrieval-Augmented Generation (RAG) system that runs entirely on consumer hardware (even 4GB GPUs). It allows you to upload private PDFs, organise them into folders, rename and move documents, and then ask questions with **exact page citations** – all without sending any data to the cloud.

> ✅ **Portfolio project** – Demonstrates hybrid search (BM25 + vector), hardware‑aware optimisation, OCR fallback for scanned PDFs, and a full‑featured document management UI.

---

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| **Hybrid Search** | Combines dense vector search (all‑MiniLM‑L6‑v2) with BM25 keyword search (Whoosh) via weighted RRF (α=0.1). |
| **Page‑Aware Citations** | Extracts and preserves page numbers using `pdfplumber` + regex fallback; never shows empty `(p. )`. |
| **Document Management** | Full CRUD interface at `/documents` – upload, rename, move between folders, delete with confirmation. |
| **Folder Organisation** | Categorise documents into custom folders, filter by folder, and migrate files across folders. |
| **Live System Dashboard** | Click the status indicator in the header to see GPU VRAM usage, active models, and last query latency (retrieval + synthesis). |
| **Dark / Light Mode** | Persistent theme toggle (sun/moon) using `next-themes` – respects system preference. |
| **OCR Fallback** | Scanned PDFs (no text layer) are processed via Tesseract OCR page‑by‑page. |
| **Air‑Gapped Ready** | Runs completely offline using local Ollama models – no external API calls. |
| **exFAT Compatibility** | Custom Node.js patch enables building on Windows exFAT drives (common for removable SSDs). |

---

## 📊 Performance Benchmarks (4GB GPU – GTX 1650)

All measurements on a 12‑page PDF (`Top 10 Ways The Rundown Uses AI.pdf`) with optimised settings (CPU embeddings, `top_k=3`, warm model):

| Query | Total Latency | Retrieval | Synthesis | VRAM |
|-------|--------------|-----------|-----------|------|
| *What does The Rundown use Granola for?* (cold) | 22.3s | 0.62s | 21.7s | 2364 MiB |
| *How did Rowan grow his Instagram account?* (warm) | 8.36s | 0.09s | 8.27s | 2364 MiB |
| *Granola* (warm) | 12.89s | 0.04s | 12.85s | 2364 MiB |
| *List the top 3 ways The Rundown uses AI.* | 6.45s | 0.04s | 6.41s | 2364 MiB |
| *What is the capital of France?* (out‑of‑context) | 2.18s | 0.09s | 2.10s | 2364 MiB |

> **Warm queries** (models already in VRAM) average **8‑12 seconds** – interactive enough for a local prototype.  
> **Cached queries** (identical questions) return instantly (<0.1s) via `lru_cache`.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI (Python 3.10+) |
| **Vector Database** | ChromaDB (persistent) |
| **Keyword Index** | Whoosh (BM25) |
| **Embeddings** | all‑MiniLM‑L6‑v2 via `sentence-transformers` (CPU) |
| **Chat LLM** | qwen2.5:3b-instruct-q4_1 via Ollama (GPU) |
| **PDF Parsing** | `pdfplumber` + Tesseract OCR |
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| **State / Theme** | `next-themes` for dark mode |
| **Database** | SQLite (fallback) / PostgreSQL (optional) |

---

## 📦 Setup Instructions

### 1. Prerequisites

- **Python** 3.10 – 3.13  
- **Node.js** 22+  
- **Ollama** (running locally)  
- **Tesseract OCR** (for scanned PDFs) – [Download for Windows](https://github.com/UB-Mannheim/tesseract/wiki) – install to `C:\Program Files\Tesseract-OCR` and add to PATH.

### 2. Clone & Install

```bash
git clone https://github.com/your-username/VaultRAG.git
cd VaultRAG
```

### 3. Backend Setup

```bash
python -m venv venv
source venv/bin/activate      # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt

# Pull Ollama models
ollama pull qwen2.5:3b-instruct-q4_1
ollama pull all-minilm:l6-v2   # embeddings (used via sentence-transformers)
```

Create `.env` (copy `.env.example`):

```ini
USE_LOCAL_LLM=true
LOCAL_LLM_MODEL=qwen2.5:3b-instruct-q4_1
EMBEDDING_MODEL=all-minilm:l6-v2
```

Run the backend:

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev   # starts on http://localhost:3000
```

> **Windows exFAT users**: The project includes a patch (`patch-readlink.js`) that automatically resolves a Webpack build error. No extra steps needed.

### 5. (Optional) Tesseract OCR for Scanned PDFs

Install Tesseract as linked above, then verify:

```bash
tesseract --version
```

The system will automatically fall back to OCR when `pdfplumber` extracts less than 200 characters from a page.

---

## 🖥️ Usage Guide

### Upload & Organise Documents

- Go to **Manage Document Vault** (sidebar button) → `/documents` page.
- Create a folder (e.g., “HR Policies” or “Financial Reports”).
- Upload PDFs – select a target folder during upload.
- Rename documents, move them between folders, or delete with confirmation.

### Chat with Your Documents

- Go back to the main chat page (`/`).
- Ask questions naturally, e.g., *“What does Granola do?”*
- The answer will include a citation badge showing the filename and page number.
- Hover over the badge to see the exact source snippet.

### Monitor System Health

- Click the status indicator in the top‑right corner.
- View live GPU VRAM usage, active models, and the latency breakdown of the last query.

### Dark Mode

- Click the sun/moon icon in the header to toggle persistent dark / light theme.

---

## 🧪 Testing

Run backend tests:

```bash
python -m pytest
```

Expected output: **3 passed** (unit tests for API, ingestion, retrieval).

Run frontend type check:

```bash
cd frontend
npx tsc --noEmit
```

---

## 🚧 Known Limitations & Future Roadmap

| Limitation | Why It Exists | Planned Solution |
|------------|---------------|------------------|
| No multi‑user / authentication | Single‑user prototype | Add JWT + role‑based access (optional, out of scope) |
| No full‑text search across folders | Folder filter only | Add Elasticsearch / Meilisearch integration |
| Large PDFs (>100 pages) slow | ChromaDB local performance | Migrate to Qdrant or Weaviate cluster |
| No support for image‑only PDFs without OCR | Requires Tesseract | Already implemented – works for scanned pages |

**Scaling to production** would require:
- Replacing ChromaDB with a distributed vector store (Qdrant / Pinecone).
- Adding asynchronous task queues (Celery) for batch ingestion.
- Implementing WebSocket streaming for real‑time progress.

---

## 🤝 Contributing

See `CONTRIBUTING.md` for development guidelines.  
All contributions must pass `pytest` and `npm run build`.

---

## 📄 License

MIT – free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- Built with [LlamaIndex](https://www.llamaindex.ai/), [Ollama](https://ollama.com/), [Next.js](https://nextjs.org/), and [Tailwind CSS](https://tailwindcss.com/).  
- OCR support via [Tesseract](https://github.com/tesseract-ocr/tesseract).
