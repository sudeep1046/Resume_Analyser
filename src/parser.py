import io
import pdfplumber

def extract_text_from_pdf_bytes(file_bytes):
    text = ""
    # Wrap bytes in BytesIO so pdfplumber can seek
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()
