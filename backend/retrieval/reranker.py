from typing import List, Optional
from llama_index.core.postprocessor import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore

class PassThroughReranker(BaseNodePostprocessor):
    """Does nothing – serves as a placeholder. Replace with local SentenceTransformerRerank if needed."""
    
    @classmethod
    def class_name(cls) -> str:
        return "PassThroughReranker"
    
    def _postprocess_nodes(
        self, nodes: List[NodeWithScore], query_bundle: Optional[dict] = None
    ) -> List[NodeWithScore]:
        return nodes

# Optional: Enable local reranking by uncommenting below (requires sentence-transformers)
# from llama_index.postprocessor import SentenceTransformerRerank
# def get_local_reranker(top_k: int = 3) -> SentenceTransformerRerank:
#     return SentenceTransformerRerank(model="cross-encoder/ms-marco-MiniLM-L-6-v2", top_n=top_k)