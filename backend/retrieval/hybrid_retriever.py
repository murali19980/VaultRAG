import logging
from functools import lru_cache
from typing import Dict, List, Optional

from llama_index.core import VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore, QueryBundle, TextNode
from llama_index.vector_stores.chroma import ChromaVectorStore

from backend.retrieval.bm25_index import BM25Index

logger = logging.getLogger(__name__)


class HybridRetriever(BaseRetriever):
    def __init__(
        self,
        vector_store: ChromaVectorStore,
        bm25_index: BM25Index,
        embed_model: BaseEmbedding,
        similarity_top_k: int = 5,
        bm25_top_k: int = 5,
        rrf_k: int = 60,
        final_top_k: int = 3,
        alpha: float = 0.1,  # 10% dense (vector), 90% sparse (BM25) for proper noun accuracy
    ) -> None:
        self._vector_store = vector_store
        self._bm25_index = bm25_index
        self._embed_model = embed_model
        self._similarity_top_k = similarity_top_k
        self._bm25_top_k = bm25_top_k
        self._rrf_k = rrf_k
        self._final_top_k = final_top_k
        self._alpha = alpha
        super().__init__()

    @classmethod
    def class_name(cls) -> str:
        return "HybridRetriever"

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        # Return a mutable list from the cached immutable tuple
        return list(self._retrieve_cached(query_bundle.query_str))

    @lru_cache(maxsize=128)
    def _retrieve_cached(self, query_str: str) -> tuple:
        import re
        logger.info(
            "Running uncached hybrid retrieve for query: '%s' (dense=%d, bm25=%d, alpha=%.2f)",
            query_str,
            self._similarity_top_k,
            self._bm25_top_k,
            self._alpha,
        )

        file_filter = None
        match = re.search(r'\[DOC:\s*(.*?)\]', query_str)
        if match:
            file_filter = match.group(1).strip()
            query_str = re.sub(r'\[DOC:\s*(.*?)\]', '', query_str).strip()
            logger.info("Filtering hybrid search by document: '%s'", file_filter)

        query_bundle = QueryBundle(query_str=query_str)
        index = VectorStoreIndex.from_vector_store(
            self._vector_store, embed_model=self._embed_model
        )
        chroma_retriever = index.as_retriever(
            similarity_top_k=self._similarity_top_k
        )
        chroma_results: List[NodeWithScore] = chroma_retriever.retrieve(query_bundle)
        if file_filter:
            chroma_results = [
                n for n in chroma_results 
                if n.node.metadata.get("file_name") == file_filter
            ]
        logger.debug("Chroma returned %d results", len(chroma_results))

        bm25_raw = self._bm25_index.search(query_str, top_k=self._bm25_top_k)
        if file_filter:
            bm25_raw = [
                doc for doc in bm25_raw 
                if doc.get("metadata", {}).get("file_name") == file_filter
            ]
        logger.debug("BM25 returned %d results", len(bm25_raw))

        node_map: Dict[str, NodeWithScore] = {}
        rrf_scores: Dict[str, float] = {}

        for rank, nws in enumerate(chroma_results, start=1):
            nid = nws.node.node_id
            node_map[nid] = nws
            rrf_scores[nid] = rrf_scores.get(nid, 0) + self._alpha * (1.0 / (self._rrf_k + rank))

        for rank, doc in enumerate(bm25_raw, start=1):
            nid = doc["doc_id"]
            rrf_scores[nid] = rrf_scores.get(nid, 0) + (1.0 - self._alpha) * (1.0 / (self._rrf_k + rank))
            if nid not in node_map:
                text_node = TextNode(
                    text=doc["text"],
                    metadata=doc.get("metadata", {}),
                    node_id=nid,
                )
                node_map[nid] = NodeWithScore(node=text_node, score=0.0)

        sorted_ids = sorted(
            rrf_scores, key=rrf_scores.get, reverse=True
        )[: self._final_top_k]

        results: List[NodeWithScore] = []
        for nid in sorted_ids:
            nws = node_map[nid]
            nws.score = rrf_scores[nid]
            results.append(nws)

        logger.info("Hybrid retrieve returned %d results", len(results))
        return tuple(results)
