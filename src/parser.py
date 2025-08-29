from typing import List
import fitz  # PyMuPDF

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """Extract plain text from a PDF given as bytes using PyMuPDF."""
    text_chunks: List[str] = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            page_text = page.get_text("text") or ""
            text_chunks.append(page_text)
    return "\n".join(text_chunks)
