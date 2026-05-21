from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pathlib import Path
from sqlalchemy.orm import Session
import shutil

from app.database import get_db
from app.models import Document, DocumentChunk
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
def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).order_by(Document.uploaded_at.desc()).all()

    return {
        "documents": [
            {
                "id": documents.id,
                "filename": documents.filename,
                "content_type": documents.content_type,
                "file_path": documents.file_path,
                "text_length": documents.text_length,
                "chunk_count": documents.chunk_count,
                "uploaded_at": documents.uploaded_at.isoformat()
            }
            for documents in documents
        ]
    }

## Endpoint to check the status of the document service
@router.get("/status")
def get_status():
    return {
        "document_service": "ready" 
    }

## Endpoint to handle document uploads
@router.post("/upload")
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
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

    document = Document(
        filename=file.filename,
        content_type=file.content_type or "application/pdf",
        file_path=str(file_path),
        text_length=len(extracted_text),
        chunk_count=len(chunks)
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    for index, chunk in enumerate(chunks):
        document_chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=index,
            content=chunk
        )
        db.add(document_chunk)
    
    db.commit()

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