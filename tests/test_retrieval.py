import tempfile
from backend.retrieval.bm25_index import BM25Index, delete_document_from_bm25

def test_bm25_index_crud():
    with tempfile.TemporaryDirectory() as tmpdir:
        bm25 = BM25Index(index_path=tmpdir)
        
        # Test adding documents
        docs = [
            {"doc_id": "1", "text": "VaultRAG is a secure enterprise knowledge base.", "metadata": {"file_name": "intro.pdf"}},
            {"doc_id": "2", "text": "It uses hybrid vector search and BM25 index with RRF.", "metadata": {"file_name": "architecture.pdf"}},
        ]
        bm25.add_documents(docs)
        
        # Test search
        results = bm25.search("hybrid", top_k=5)
        assert len(results) >= 1
        assert results[0]["doc_id"] == "2"
        assert results[0]["metadata"]["file_name"] == "architecture.pdf"

        # Test deletion from BM25
        delete_document_from_bm25(doc_id="2", index_path=tmpdir)

        # Search again – doc 2 should be gone
        results_after = bm25.search("hybrid", top_k=5)
        assert len(results_after) == 0