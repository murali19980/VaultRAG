from llama_index.core.schema import Document
from backend.ingestion.chunker import contextual_chunking

def test_contextual_chunking():
    doc = Document(
        text="This is a normal paragraph.\n\n"
             "| Header 1 | Header 2 |\n"
             "| --- | --- |\n"
             "| Value 1 | Value 2 |\n\n"
             "Another normal text line.\n\n"
             "```python\n"
             "print('Hello, VaultRAG!')\n"
             "```"
    )
    nodes = contextual_chunking([doc], chunk_size=512, chunk_overlap=50)
    assert len(nodes) >= 3
    
    # Check if table node was processed separately
    table_nodes = [n for n in nodes if n.metadata.get("is_table") is True]
    assert len(table_nodes) >= 1
    assert "Header 1" in table_nodes[0].text