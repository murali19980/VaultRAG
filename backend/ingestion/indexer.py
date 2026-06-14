import logging

from llama_index.core import StorageContext, VectorStoreIndex

from backend.ingestion.chunker import contextual_chunking
from backend.ingestion.embeddings import get_embedding_model
from backend.ingestion.loader import load_documents
from backend.retrieval.bm25_index import BM25Index, BM25_PATH
from backend.retrieval.vector_store import get_chroma_vector_store

logger = logging.getLogger(__name__)


def run_ingestion(
    input_dir: str = "uploads",
    chroma_collection: str = "vaultrag",
    bm25_path: str = BM25_PATH,
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
    input_files: list[str] = None,
    folder: str = "Default",
) -> int:
    import glob
    import os

    if input_files:
        logger.info("Starting ingestion of %d specific file(s)", len(input_files))
        files_to_load = input_files
    else:
        logger.info("Starting ingestion from '%s'", input_dir)
        files_to_load = []
        extensions = [".pdf", ".xlsx", ".xls", ".docx", ".csv"]
        for ext in extensions:
            pattern = os.path.join(input_dir, "**", f"*{ext}")
            files_to_load.extend(glob.glob(pattern, recursive=True))

    try:
        documents = load_documents(files_to_load)
    except Exception:
        logger.exception("Failed to load documents")
        raise

    if not documents:
        if input_files:
            logger.warning("No documents loaded from file list")
        else:
            logger.warning("No documents found in '%s'", input_dir)
        return 0

    logger.info("Loaded %d document(s)", len(documents))

    nodes = contextual_chunking(
        documents,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    if not nodes:
        logger.warning("Chunking produced zero nodes")
        return 0

    # Apply folder tag to metadata
    for node in nodes:
        node.metadata["folder"] = folder or "Default"

    logger.info("Created %d chunk(s)", len(nodes))

    embed_model = get_embedding_model()

    try:
        logger.info("Building VectorStoreIndex into Chroma…")
        vector_store = get_chroma_vector_store(collection_name=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        VectorStoreIndex(
            nodes=nodes,
            storage_context=storage_context,
            embed_model=embed_model,
            show_progress=True,
        )
    except Exception:
        logger.exception("Failed to index nodes into Chroma")
        raise

    try:
        logger.info("Indexing into Whoosh BM25…")
        bm25 = BM25Index(index_path=bm25_path)
        bm25_docs = [
            {
                "doc_id": node.node_id,
                "text": node.text,
                "metadata": node.metadata,
            }
            for node in nodes
        ]
        bm25.add_documents(bm25_docs)
    except Exception:
        logger.exception("Failed to index nodes into Whoosh BM25")
        raise

    try:
        from backend.api.chat import _get_or_create_query_engine
        engine = _get_or_create_query_engine()
        if hasattr(engine.retriever, "_retrieve_cached"):
            logger.info("Clearing query engine cache post-ingestion...")
            engine.retriever._retrieve_cached.cache_clear()
    except Exception:
        logger.exception("Failed to clear query cache post-ingestion")

    logger.info("Ingestion complete – %d node(s) indexed", len(nodes))
    return len(nodes)
