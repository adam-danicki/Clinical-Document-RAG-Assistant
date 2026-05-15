from pathlib import Path
from pypdf import PdfReader

## Service to extract text from PDF files
def extract_text_from_pdf(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    reader = PdfReader(str(path))
    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text_parts.append(page_text)
        
    
    return "\n\n".join(text_parts)