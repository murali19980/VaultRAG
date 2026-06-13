import logging
import re
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

def extract_citations(response) -> List[Dict[str, Any]]:
    """
    Extract citations from response source nodes.
    If page_label is missing or N/A, attempts to infer it from context text using regex fallbacks.
    """
    seen: set[Tuple[str, str]] = set()
    citations: List[Dict[str, Any]] = []

    if not response or not hasattr(response, "source_nodes") or not response.source_nodes:
        return citations

    for node_with_score in response.source_nodes:
        node = node_with_score.node
        page = node.metadata.get("page_label")
        file_name = node.metadata.get("file_name", "unknown")
        snippet = node.get_content()[:200]

        # Fallback 1: Search for page indicators inside the text segment
        if not page or str(page).strip().lower() in ["", "none", "n/a"]:
            text = node.get_content()[:500]
            match = re.search(r'(?:Page|p\.|page)\s*(\d+)', text, re.IGNORECASE)
            if match:
                page = match.group(1)

        # Fallback 2: Visual placeholder instead of empty string
        if not page or str(page).strip().lower() in ["", "none", "n/a"]:
            page = "?"

        page_str = str(page).strip()
        key = (page_str, file_name)
        if key in seen:
            continue
        seen.add(key)

        citations.append(
            {
                "page": page_str,
                "file": file_name,
                "snippet": snippet,
            }
        )

    logger.info("Extracted %d unique citations", len(citations))
    return citations
