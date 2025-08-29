import io
import fitz  # PyMuPDF

def extract_text_from_pdf_bytes(file_bytes):
    with fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text
