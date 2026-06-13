import logging
from typing import Optional, Union

from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import CompactAndRefine
from llama_index.core.retrievers import BaseRetriever
from llama_index.llms.ollama import Ollama
from llama_index.llms.openrouter import OpenRouter

from backend.config import (
    LOCAL_LLM_MODEL,
    OLLAMA_BASE_URL,
    OPENROUTER_API_KEY,
    USE_LOCAL_LLM,
)
from backend.qa.prompt_templates import QA_PROMPT, REFINE_PROMPT

logger = logging.getLogger(__name__)


def _get_llm():
    if USE_LOCAL_LLM:
        logger.info("Using local Ollama LLM: %s", LOCAL_LLM_MODEL)
        return Ollama(
            model=LOCAL_LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            request_timeout=120.0,
        )
    logger.info("Using OpenRouter LLM")
    return OpenRouter(
        api_key=OPENROUTER_API_KEY,
        model="gpt-4o-mini",
        temperature=0.1,
    )


def get_query_engine(
    retriever: BaseRetriever,
    llm: Optional[Union[Ollama, OpenRouter]] = None,
) -> RetrieverQueryEngine:
    if llm is None:
        llm = _get_llm()
    synthesizer = CompactAndRefine(
        llm=llm,
        streaming=False,
        text_qa_template=QA_PROMPT,
        refine_template=REFINE_PROMPT,
    )
    engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=synthesizer,
    )
    logger.info("Query engine created with retriever=%s", type(retriever).__name__)
    return engine
