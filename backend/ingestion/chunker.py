import re
import logging
from typing import List, Tuple

from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.schema import Document, TextNode

logger = logging.getLogger(__name__)


def _is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2


def _is_code_block(text: str) -> bool:
    t = text.strip()
    return t.startswith("```") and t.endswith("```") and t.count("```") == 2


def _preserve_special_regions(text: str) -> List[Tuple[str, bool, bool]]:
    segments: List[Tuple[str, bool, bool]] = []
    code_pattern = re.compile(r"(```[\s\S]*?```)", re.MULTILINE)
    parts = code_pattern.split(text)

    for part in parts:
        if not part:
            continue
        if _is_code_block(part):
            segments.append((part, False, True))
            continue
        lines = part.split("\n")
        i = 0
        while i < len(lines):
            if _is_table_line(lines[i]):
                table_lines: List[str] = []
                while i < len(lines) and _is_table_line(lines[i]):
                    table_lines.append(lines[i])
                    i += 1
                if table_lines:
                    segments.append(("\n".join(table_lines), True, False))
            else:
                normal_lines: List[str] = []
                while i < len(lines) and not _is_table_line(lines[i]):
                    normal_lines.append(lines[i])
                    i += 1
                if normal_lines:
                    segments.append(("\n".join(normal_lines), False, False))
    return segments


def contextual_chunking(
    documents: List[Document],
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
) -> List[TextNode]:
    if not documents:
        logger.warning("contextual_chunking called with empty document list")
        return []

    all_nodes: List[TextNode] = []
    parser = HierarchicalNodeParser.from_defaults(
        chunk_sizes=[chunk_size * 2, chunk_size],
        chunk_overlap=chunk_overlap,
    )

    for doc in documents:
        try:
            base_metadata = dict(doc.metadata)
            page_label = base_metadata.get("page_label")
            segments = _preserve_special_regions(doc.text)

            for text, is_table, is_code in segments:
                if not text.strip():
                    continue
                if is_table or is_code:
                    node = TextNode(
                        text=text,
                        metadata={
                            **base_metadata,
                            "is_table": is_table,
                            "page_label": page_label,
                        },
                    )
                    all_nodes.append(node)
                else:
                    nodes = parser.get_nodes_from_documents(
                        [Document(text=text, metadata=base_metadata)]
                    )
                    leafs = get_leaf_nodes(nodes)
                    for leaf in leafs:
                        leaf.metadata["is_table"] = False
                        if page_label:
                            leaf.metadata["page_label"] = page_label
                        all_nodes.append(leaf)
        except Exception:
            logger.exception("Failed to chunk document: %s", getattr(doc, "doc_id", None))
            raise

    logger.info("Chunking complete: %d nodes from %d documents", len(all_nodes), len(documents))
    return all_nodes
