import logging

import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from backend.config import CHROMA_COLLECTION

logger = logging.getLogger(__name__)

CHROMA_PATH = "chroma_db"


def get_chroma_vector_store(collection_name: str = CHROMA_COLLECTION) -> ChromaVectorStore:
    logger.info(
        "Opening Chroma persistent client at '%s', collection='%s'",
        CHROMA_PATH,
        collection_name,
    )
    try:
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        chroma_collection = chroma_client.get_or_create_collection(collection_name)
        return ChromaVectorStore(chroma_collection=chroma_collection)
    except Exception:
        logger.exception("Failed to initialise Chroma vector store")
        raise


def get_chroma_collection(collection_name: str = CHROMA_COLLECTION):
    logger.info(
        "Returning raw Chroma collection '%s' from '%s'",
        collection_name,
        CHROMA_PATH,
    )
    try:
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        return chroma_client.get_or_create_collection(collection_name)
    except Exception:
        logger.exception("Failed to get Chroma collection")
        raise
