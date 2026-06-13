import logging
from typing import List, Any
from llama_index.core.embeddings import BaseEmbedding
from pydantic import PrivateAttr
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class LocalSentenceTransformerEmbedding(BaseEmbedding):
    _model: Any = PrivateAttr()

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        logger.info("Loading sentence-transformers model '%s' on CPU (no VRAM used)...", model_name)
        self._model = SentenceTransformer(model_name, device="cpu")

    @classmethod
    def class_name(cls) -> str:
        return "LocalSentenceTransformerEmbedding"

    def _get_query_embedding(self, query: str) -> List[float]:
        return self._model.encode(query, convert_to_numpy=True).tolist()

    def _get_text_embedding(self, text: str) -> List[float]:
        return self._model.encode(text, convert_to_numpy=True).tolist()

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._model.encode(texts, convert_to_numpy=True).tolist()

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)

def get_embedding_model() -> LocalSentenceTransformerEmbedding:
    return LocalSentenceTransformerEmbedding()
