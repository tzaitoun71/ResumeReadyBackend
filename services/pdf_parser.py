import fitz

def extract_text_from_pdf(file_path: str) -> str:
    try:
        with fitz.open(file_path) as pdf:
            text = ""
            for page in pdf:
                text += page.get_text()
            return text.strip()
    except Exception as e:
        print(f"Error extracting text from pdf: {e}")
        return ""