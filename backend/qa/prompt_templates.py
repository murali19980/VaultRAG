from llama_index.core import PromptTemplate

# Standard QA template that forces citations
qa_template_str = (
    "You are a helpful assistant for enterprise documents. "
    "Answer the question based ONLY on the following context. "
    "For each factual claim, cite the source file and page number in parentheses, e.g. (HR_Manual.pdf, p.12). "
    "If the answer is not in the context, say 'I cannot find that information in the provided documents.'\n"
    "---------------------\n"
    "Context: {context_str}\n"
    "---------------------\n"
    "Question: {query_str}\n"
    "Answer: "
)

QA_PROMPT = PromptTemplate(qa_template_str)

# You can also define a REFINE template if needed
refine_template_str = (
    "The original answer is: {existing_answer}\n"
    "We have the opportunity to refine it with more context.\n"
    "Context: {context_msg}\n"
    "Refine the answer, preserving citations when possible.\n"
    "New answer: "
)
REFINE_PROMPT = PromptTemplate(refine_template_str)