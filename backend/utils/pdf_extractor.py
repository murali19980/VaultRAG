import os
import logging
import platform
import pytesseract
from typing import Dict

logger = logging.getLogger(__name__)

# Configure Tesseract path on Windows if needed
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# In-memory OCR cache for page contents
_ocr_page_cache: Dict[str, str] = {}

def extract_page_ocr(pdf_path: str, page_number: int) -> str:
    """
    Run Tesseract OCR on a specific page of a PDF file using pdf2image.
    """
    cache_key = f"{pdf_path}_{page_number}"
    if cache_key in _ocr_page_cache:
        logger.info("Using cached OCR result for %s page %d", os.path.basename(pdf_path), page_number)
        return _ocr_page_cache[cache_key]

    try:
        from pdf2image import convert_from_path
        logger.info("Running Tesseract OCR on page %d of %s...", page_number, os.path.basename(pdf_path))
        # Render only the target page to optimize performance
        images = convert_from_path(pdf_path, dpi=150, first_page=page_number, last_page=page_number)
        if images:
            text = pytesseract.image_to_string(images[0])
            _ocr_page_cache[cache_key] = text
            return text
    except Exception as e:
        logger.error("OCR failed for %s page %d: %s", pdf_path, page_number, str(e))
    
    return ""
