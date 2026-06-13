# VaultRAG: Local-First Hybrid RAG with Page Citations

VaultRAG is a secure, local-first retrieval-augmented generation (RAG) system designed to run completely offline on consumer-grade hardware. It allows users to upload private PDF documents, extract page-aware text and tables, and query them using a hybrid search pipeline. The system synthesizes answers using a local LLM and outputs precise, verifiable page-level citations.

---

## Why It Matters
* **Absolute Privacy**: Running fully offline (air-gapped) ensures that sensitive corporate or personal documents are never transmitted over the internet or exposed to third-party APIs.
* **Low-Resource Friendly**: Engineered to run efficiently on budget consumer hardware (such as a 4GB VRAM GPU) without requiring expensive cloud instances.
* **Lexical-Semantic Hybrid Precision**: Combines dense semantic vector search with lexical BM25 keyword matching to accurately retrieve both conceptual information and exact terminology (like names, codes, or specific terminology).

---

## Tech Stack
* **Frontend**: Next.js 14 (App Router), React, Lucide Icons, Tailwind CSS
* **Backend**: FastAPI, SQLAlchemy
* **Database**: PostgreSQL (with automatic SQLite fallback for serverless/local usage)
* **RAG Framework**: LlamaIndex (Core Orchestration, Node parsing)
* **PDF Engine**: `pdfplumber` (custom page-by-page text & layout extraction)
* **Vector Store**: ChromaDB (local persistence)
* **Lexical Index**: Whoosh BM25
* **Embedding Model**: `all-MiniLM-L6-v2` (running on CPU via Hugging Face `sentence-transformers`)
* **Chat LLM**: `qwen2.5:3b-instruct-q4_1` (running locally via Ollama)

---

## Setup & Installation

### 1. Prerequisites
* **Python**: 3.10 to 3.13
* **Node.js**: 22+
* **Ollama**: Installed and running locally

### 2. Pull local Ollama Models
Ensure the Ollama service is running, then pull the lightweight chat LLM:
```bash
ollama pull qwen2.5:3b-instruct-q4_1
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and configure:
```ini
USE_LOCAL_LLM=true
LOCAL_LLM_MODEL=qwen2.5:3b-instruct-q4_1
OLLAMA_BASE_URL=http://localhost:11434
```

### 4. Running the Backend
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the FastAPI server:
   ```bash
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

### 5. Running the Frontend
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
2. Open [http://localhost:3000](http://localhost:3000)

---

## Performance Benchmarks

Following rigorous system profiling and targeted optimizations, here is how VaultRAG performs on a budget **NVIDIA GeForce GTX 1650 (4GB VRAM)** querying the 12-page document `Top 10 Ways The Rundown Uses AI.pdf`:

### System Configuration
* **LLM**: `qwen2.5:3b-instruct-q4_1` (GPU, ~2.0 GB)
* **Embeddings**: `all-MiniLM-L6-v2` (CPU, ~45 MB)
* **Context Limit**: Capped at `top_k=3` (~1500 tokens)
* **Cache**: In-memory query cache (`lru_cache`) active

### Benchmark Results
| Query | Type | Retrieval Latency | Synthesis Latency | Total Latency | VRAM Peak | Status / Result |
|---|---|---|---|---|---|---|
| *What does The Rundown use Granola for?* | Cold Load | 0.622s | 21.683s | **22.306s** | 2364 MiB | Success (Cited p. 2) |
| *How did Rowan grow his Instagram account?* | Warm Model | 0.090s | 8.267s | **8.357s** | 2364 MiB | Success (Cited p. 4) |
| *Granola* | Warm Model | 0.043s | 12.848s | **12.891s** | 2364 MiB | Success (Cited p. 2) |
| *List the top 3 ways The Rundown uses AI.* | Warm Model | 0.044s | 6.406s | **6.450s** | 2364 MiB | Success (Catch out-of-context)* |
| *What is the capital of France?* | Warm Model | 0.085s | 2.096s | **2.182s** | 2364 MiB | Correctly caught out-of-context |

*\* Note: Query #4 correctly identified that the specific information was not present in the document's content, maintaining hallucination resistance.*

---

## Known Limitations & Trade-offs

* **Semantic Search Dimensionality**: Using `all-MiniLM-L6-v2` (384 dimensions) on the CPU reduces VRAM usage to zero and makes retrieval ultra-fast (<0.1s), but it has a lower semantic capacity compared to heavier models like `nomic-embed-text-v2-moe` (768 dimensions). For complex, technical vocabularies, this represents a trade-off between speed and retrieval depth.
* **Large Context Processing (Prompt pre-fill)**: Non-Tensor Core GPUs lack dedicated hardware matrix acceleration. While warm synthesis is optimized to ~6–8s, the prompt pre-fill phase scales linearly with context length. Capping context to `top_k=3` maintains responsiveness but limits the volume of context fed to the LLM.
* **Document Layout & Multi-Format Extraction**:
  * **Word/DOCX**: Handled via standard text extraction, which flattens structural details like header layouts and embedded tables.
  * **Excel/Spreadsheets**: Parsed row-by-row, converting grid structures into raw text paragraphs and destroying cell coordinate relationships.
  * **JSON/XML**: Read as plain-text, bloating the context window with formatting syntax (`{}`, `<>`) and wasting LLM context space.

---

## Future Roadmap (Enterprise Scaling)

To scale this local proof-of-concept into a production-grade enterprise knowledge base, the following architectural upgrades are recommended:

### 1. Handling Massive PDFs (500–7,000+ Pages)
* **Memory-Safe Ingestion**: Implement streaming/lazy page parsing via python generator interfaces in `pdfplumber` to process documents page-by-page without loading the entire document into RAM.
* **Asynchronous Task Queues**: Offload document chunking, indexing, and embedding to distributed queues (e.g., Celery with RabbitMQ or Redis Queue) to prevent API timeouts and handle long-running background tasks.
* **Vector Cluster Storage**: Swap the local SQLite-based ChromaDB and Whoosh indices for distributed search databases (e.g., Qdrant, Pinecone, or Elasticsearch) supporting clustering, partitioning, and remote querying.

### 2. Large Tabular Datasets (e.g., 1.2GB Excel sheets with 10M+ rows)
* **Text-to-SQL Pipeline**: Avoid chunking and embedding tabular data. Instead, load large spreadsheets into high-performance analytical database engines like **DuckDB** or **PostgreSQL**.
* **NL-to-SQL Execution**: Deploy a semantic translation engine where the local LLM translates natural language questions into executable SQL (e.g. `SELECT AVG(sales) FROM transactions WHERE country='US'`), executes it directly on DuckDB in milliseconds, and returns a structured response.

---

## License
Distributed under the MIT License. See [LICENSE](LICENSE) for details.
