from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pathlib import Path
from sqlalchemy.orm import Session
import shutil
import math

from app.database import get_db

from app.models import Document, DocumentChunk

from app.schemas import SearchRequest, AskRequest

from app.services.pdf_parser import extract_text_from_pdf
from app.services.chunker import chunk_text
from app.services.embeddings import create_embedding
from app.services.rag import generate_answer



## Router for document-related endpoints
router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


## Directory to store uploaded documents
## Create the directory if it doesn't exist
UPLOAD_DIR = Path("app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

## Helper function to calculate dynamic top_k based on total chunks
def calculate_dynamic_top_k(total_chunks: int, min_k: int = 5, max_k: int = 40, ratio: float = 0.05) -> int:
    if total_chunks <= 0:
        return min_k
    return min(max_k, max(min_k, math.ceil(total_chunks * ratio)))


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


## Endpoint to get details of a specific document by ID
@router.get("/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": document.id,
        "filename": document.filename,
        "content_type": document.content_type,
        "file_path": document.file_path,
        "text_length": document.text_length,
        "chunk_count": document.chunk_count,
        "uploaded_at": document.uploaded_at.isoformat()
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
        embedding = create_embedding(chunk)

        document_chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=index,
            content=chunk,
            embedding=embedding
        )
        db.add(document_chunk)
    
    db.commit()

    return {
        "message": "File uploaded, parsed, chunked, embedded, and saved successfully",
        "document_id": document.id,
        "filename": document.filename,
        "content_type": document.content_type,
        "file_path": document.file_path,
        "text_length": document.text_length,
        "chunk_count": document.chunk_count,
        "embeddings_created": len(chunks),
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "first_chunk_preview": chunks[0][:500] if chunks else None
    }


## Endpoint to delete a file from the backend
@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = Path(document.file_path)
    if file_path.exists():
        file_path.unlink()
    
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
    
    db.delete(document)
    db.commit()
    
    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
        "filename": document.filename
    }


## Endpoint to search documents based on a question and return relevant chunks
@router.post("/search")
def search_documents(request: SearchRequest,db: Session = Depends(get_db)):
    question_embedding = create_embedding(request.question)
    total_chunks = db.query(DocumentChunk).count()
    top_k = request.top_k if request.top_k and request.top_k > 0 else calculate_dynamic_top_k(total_chunks)

    results = (
        db.query(DocumentChunk, Document)
        .join(Document, DocumentChunk.document_id == Document.id)
        .filter(DocumentChunk.embedding != None)
        .order_by(DocumentChunk.embedding.cosine_distance(question_embedding))
        .limit(top_k)
        .all()
    )

    return {
        "question": request.question,
        "top_k": top_k,
        "total_chunks": total_chunks,
        "results": [
            {
                "document_id": document.id,
                "filename": document.filename,
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "content_preview": chunk.content[:500],
            }
            for chunk, document in results
        ]
    }


## Endpoint to ask a question and get an answer based on the uploaded documents
@router.post("/ask")
def ask_documents(request: AskRequest,db: Session = Depends(get_db)):
    question_embedding = create_embedding(request.question)
    total_chunks = db.query(DocumentChunk).count()
    top_k = request.top_k if request.top_k and request.top_k > 0 else calculate_dynamic_top_k(total_chunks)

    results = (
        db.query(DocumentChunk, Document)
        .join(Document, DocumentChunk.document_id == Document.id)
        .filter(DocumentChunk.embedding.isnot(None))
        .order_by(DocumentChunk.embedding.cosine_distance(question_embedding))
        .limit(top_k)
        .all()
    )

    context_chunks = [
        {
            "document_id": document.id,
            "filename": document.filename,
            "chunk_id": chunk.id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
        }
        for chunk, document in results
    ]

    answer = generate_answer(request.question, context_chunks)

    return {
        "question": request.question,
        "top_k": top_k,
        "total_chunks": total_chunks,
        "answer": answer,
        "sources": [
            {
                "source_number": index + 1,
                "document_id": chunk["document_id"],
                "filename": chunk["filename"],
                "chunk_id": chunk["chunk_id"],
                "chunk_index": chunk["chunk_index"],
                "content_preview": chunk["content"][:500],
            }
            for index, chunk in enumerate(context_chunks)
        ]
    }