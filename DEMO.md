# 🎥 VaultRAG Video Demo Script & Manual Walkthrough

This guide provides a step-by-step script and roadmap for demonstrating VaultRAG's features. It can be used for recording a walkthrough video or doing a live demo in an interview.

---

## 🎬 Demo Overview (approx. 2-3 minutes)

| Segment | Action | Key Talking Points |
|---------|--------|--------------------|
| **1. Intro & UI Overview** (30s) | Show the Chat Interface, toggle Dark Mode, and open the Observability Panel. | "VaultRAG is a local-first, privacy-focused RAG system optimized for lightweight GPUs." |
| **2. Document Vault** (40s) | Navigate to `/documents`, show folder sidebar, create a folder, and upload a document. | "We have a dedicated document management panel supporting custom folders for organization." |
| **3. Renaming & Moving** (40s) | Rename the document, and move it into a folder via the dropdown. | "This updates the physical file system, ChromaDB vector metadata, and the BM25 search index." |
| **4. Chat & Citation** (40s) | Ask a specific question, hover over the citation tag to view the excerpt. | "Hybrid search combines dense vector and sparse lexical retrieval, returning page-accurate citations." |

---

## 🚶 Step-by-Step Walkthrough

### Step 1: Landing Page & Custom Theme
1. Open the app in the browser at `http://localhost:3000`.
2. Notice the custom **lock/vault favicon** on your browser tab.
3. Click the **Sun / Moon Icon** in the top header to toggle between light and dark mode.
4. Click the **API Status Indicator** (pulsing green dot) in the top-right corner to open the **System Health & Observability** modal. Point out:
   - Ollama status (active models)
   - Real-time VRAM allocation (e.g., ~2.3 GiB out of 4 GiB)

---

### Step 2: Navigate to Document Manager
1. Click **Manage Document Vault** at the bottom of the sidebar.
2. You will be redirected to the `/documents` page.
3. Notice the folder sidebar on the left and the document grid on the right showing:
   - Filenames, file sizes, upload dates, and active folder categories.

---

### Step 3: Create Folders & Grouping
1. Click **"+ Add Folder"** at the bottom of the folder sidebar.
2. Enter `Product Docs` and click **Create**.
3. Now click **Upload Document** in the top right.
4. Select a PDF from your computer, choose the `Product Docs` folder from the folder dropdown, and click **Ingest**.
5. Once ingested, the document card will appear under the `Product Docs` tag in the grid.

---

### Step 4: Rename and Move Files
1. On your uploaded document card, click the **Rename** button.
2. Change the filename to `product_overview.pdf` and submit.
3. Next, click the **Move to...** folder dropdown on the card and choose a different folder (or create a new one).
4. *Self-Check*: Under the hood, this has renamed the file on disk, updated Chroma metadata, and updated the BM25 Whoosh index.

---

### Step 5: Test Citations & Fallback OCR
1. Return to the main page (click the logo/title or go to `/`).
2. Type a query, for example: `What does the product overview say about X?`
3. The response will generate. Point out the citation badges:
   - E.g., `product_overview.pdf (p. 2)`.
4. **Hover over the badge** to show the popup preview of the exact source text chunk extracted from that page.
5. *Scanned PDF Demo*: If you upload a scanned image PDF, the system automatically uses the page-by-page Tesseract OCR fallback to extract the text.

---

### Step 6: Verify Query Latency
1. Open the **API Status Indicator** again after the query finishes.
2. Point out the **Query Latency Breakdown**:
   - **Retrieval Latency**: e.g., `0.04s` (BM25 + Vector)
   - **Synthesis Latency**: e.g., `8.27s` (LLM answer generation)
   - Explain how this transparency helps developers debug system bottlenecks.
