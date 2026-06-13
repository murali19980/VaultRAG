import os
import logging
import pdfplumber
from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document
from typing import List, Optional

logger = logging.getLogger(__name__)

def load_documents(
    input_files: List[str],
) -> List[Document]:
    """
    Load specific files. PDF files are loaded using pdfplumber page-by-page 
    with native table extraction and formatting. Other formats use LlamaIndex's 
    SimpleDirectoryReader.
    """
    documents: List[Document] = []
    
    pdf_files = [f for f in input_files if f.lower().endswith(".pdf")]
    other_files = [f for f in input_files if not f.lower().endswith(".pdf")]
    
    # Process PDF files
    for pdf_path in pdf_files:
        file_name = os.path.basename(pdf_path)
        logger.info("Parsing PDF '%s' page-by-page using pdfplumber...", file_name)
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for idx, page in enumerate(pdf.pages, 1):
                    # 1. Extract text
                    text = page.extract_text() or ""
                    if len(text.strip()) < 200:
                        from backend.utils.pdf_extractor import extract_page_ocr
                        ocr_text = extract_page_ocr(pdf_path, idx)
                        if ocr_text.strip():
                            text = ocr_text
                    
                    # 2. Extract tables
                    tables = page.extract_tables()
                    table_markdowns = []
                    if tables:
                        for table in tables:
                            table_rows = []
                            for row in table:
                                if row:
                                    clean_row = [str(cell or "").strip() for cell in row]
                                    table_rows.append("| " + " | ".join(clean_row) + " |")
                            if table_rows:
                                if len(table_rows) > 1:
                                    header_len = len(table[0]) if table[0] else 0
                                    separator = "| " + " | ".join(["---"] * header_len) + " |"
                                    table_rows.insert(1, separator)
                                table_markdowns.append("\n" + "\n".join(table_rows) + "\n")
                    
                    # 3. Format and merge
                    if table_markdowns:
                        text += "\n\n### Extracted Tables:\n" + "\n".join(table_markdowns)
                    
                    if text.strip():
                        doc = Document(
                            text=text,
                            metadata={
                                "file_name": file_name,
                                "page_label": str(idx),
                                "file_path": pdf_path,
                            }
                        )
                        documents.append(doc)
            logger.info("Successfully parsed PDF '%s' into %d page nodes", file_name, len(pdf.pages))
        except Exception as e:
            logger.exception("Failed to load PDF '%s' with pdfplumber. Falling back to SimpleDirectoryReader.", pdf_path)
            try:
                reader = SimpleDirectoryReader(input_files=[pdf_path])
                documents.extend(reader.load_data())
            except Exception:
                logger.exception("Fallback reader also failed for '%s'", pdf_path)
                raise
                
    # Process other formats (docx, xls, xlsx, csv)
    if other_files:
        logger.info("Loading %d other file(s) using SimpleDirectoryReader...", len(other_files))
        try:
            reader = SimpleDirectoryReader(input_files=other_files)
            documents.extend(reader.load_data())
        except Exception:
            logger.exception("Failed to load non-PDF files")
            raise
            
    return documents