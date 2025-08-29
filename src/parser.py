import io
import fitz  # PyMuPDF

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """
    Extract text from a PDF given as bytes.
    
    :param file_bytes: PDF file content in bytes
    :return: Extracted text as a string
    """
    text = ""
    try:
        with fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text.strip()
