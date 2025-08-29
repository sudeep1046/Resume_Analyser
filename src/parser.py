import fitz  # PyMuPDF

def extract_text_from_pdf_bytes(file_obj):
    try:
        with fitz.open(stream=file_obj.read(), filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        return f"Failed to parse PDF: {e}"
