from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil

from app.services.pdf_parser import extract_text_from_pdf
from app.services.chunker import chunk_text

## Router for document-related endpoints
router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

## Directory to store uploaded documents
## Create the directory if it doesn't exist
UPLOAD_DIR = Path("app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

## Endpoint to list all uploaded documents (for testing purposes)
@router.get("/")
def list_documents():
    return {
        "documents": []
    }

## Endpoint to check the status of the document service
@router.get("/status")
def get_status():
    return {
        "document_service": "ready" 
    }

## Endpoint to handle document uploads
@router.post("/upload")
def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are supported."
        )
    
    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text_from_pdf(str(file_path))
    chunks = chunk_text(extracted_text)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "content_type": file.content_type,
        "file_path": str(file_path),
        "text_length": len(extracted_text),
        "chunk_count": len(chunks),
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "first_chunk_preview": chunks[0][:500] if chunks else None
    }