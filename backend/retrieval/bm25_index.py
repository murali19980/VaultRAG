import json
import logging
import os
from typing import Any, Dict, List

from whoosh.fields import ID, TEXT, Schema
from whoosh.index import create_in, exists_in, open_dir
from whoosh.qparser import QueryParser
from whoosh.scoring import BM25F

logger = logging.getLogger(__name__)

BM25_PATH = os.path.join("data", "bm25_index")


class BM25Index:
    def __init__(self, index_path: str = BM25_PATH):
        self.index_path = index_path
        self.schema = Schema(
            doc_id=ID(stored=True, unique=True),
            text=TEXT(stored=True),
            metadata=TEXT(stored=True),
        )
        os.makedirs(index_path, exist_ok=True)
        try:
            if not exists_in(index_path):
                self.ix = create_in(index_path, self.schema)
            else:
                self.ix = open_dir(index_path, schema=self.schema)
        except Exception:
            logger.exception("Failed to open/create Whoosh index at '%s'", index_path)
            raise

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        if not documents:
            logger.warning("add_documents called with empty list")
            return
        try:
            writer = self.ix.writer()
            for doc in documents:
                writer.update_document(
                    doc_id=str(doc["doc_id"]),
                    text=doc["text"],
                    metadata=json.dumps(doc.get("metadata", {}), default=str),
                )
            writer.commit()
            logger.info("Indexed %d documents into Whoosh BM25", len(documents))
        except Exception:
            logger.exception("Failed to write documents to BM25 index")
            raise

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        try:
            with self.ix.searcher(weighting=BM25F()) as searcher:
                parser = QueryParser("text", self.ix.schema)
                q = parser.parse(query)
                results = searcher.search(q, limit=top_k)
                return [
                    {
                        "doc_id": r["doc_id"],
                        "text": r["text"],
                        "metadata": json.loads(r["metadata"]),
                        "score": r.score,
                    }
                    for r in results
                ]
        except Exception:
            logger.exception("BM25 search failed for query: %s", query)
            raise


def build_index(documents: List[Dict[str, Any]], index_path: str = BM25_PATH) -> BM25Index:
    logger.info("Building BM25 index at '%s' with %d documents", index_path, len(documents))
    idx = BM25Index(index_path=index_path)
    idx.add_documents(documents)
    return idx


def search_index(
    query: str,
    index_path: str = BM25_PATH,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    logger.info("Searching BM25 index at '%s' for: %s", index_path, query[:80])
    idx = BM25Index(index_path=index_path)
    return idx.search(query, top_k=top_k)


def delete_document_from_bm25(doc_id: str, index_path: str = BM25_PATH) -> None:
    idx = BM25Index(index_path=index_path)
    try:
        writer = idx.ix.writer()
        writer.delete_by_term("doc_id", str(doc_id))
        writer.commit()
        logger.info("Deleted doc_id %s from BM25 index", doc_id)
    except Exception:
        logger.exception("Failed to delete doc_id %s from BM25 index", doc_id)
        raise
