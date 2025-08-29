import io
import pdfplumber

def extract_text_from_pdf_bytes(uploaded_file):
    """
    Extract text from a PDF uploaded via Streamlit.
    Handles both UploadedFile objects and raw bytes.
    """
    # Case 1: Streamlit UploadedFile
    if hasattr(uploaded_file, "read"):
        file_bytes = uploaded_file.read()
    else:
        # Already bytes
        file_bytes = uploaded_file

    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()
