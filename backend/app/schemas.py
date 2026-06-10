from datetime import datetime
from pydantic import BaseModel


## Pydantic models for request validation in API endpoints
class SearchRequest(BaseModel):
    question: str
    top_k: int | None = None


## New Pydantic model for the /ask endpoint
class AskRequest(BaseModel):
    question: str
    top_k: int | None = None


## Response models for documents API
class DocumentResponse(BaseModel):
    id: int
    filename: str
    content_type: str
    file_path: str
    text_length: int
    chunk_count: int
    uploaded_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]


class StatusResponse(BaseModel):
    document_service: str


class UploadDocumentResponse(BaseModel):
    message: str
    document_id: int
    filename: str
    content_type: str
    file_path: str
    text_length: int
    chunk_count: int
    embeddings_created: int
    chunk_size: int
    chunk_overlap: int
    first_chunk_preview: str | None = None


class DeleteDocumentResponse(BaseModel):
    message: str
    document_id: int
    filename: str


class SearchResult(BaseModel):
    document_id: int
    filename: str
    chunk_id: int
    chunk_index: int
    content_preview: str


class SearchResponse(BaseModel):
    question: str
    top_k: int
    total_chunks: int
    results: list[SearchResult]


class AskSource(BaseModel):
    source_number: int
    document_id: int
    filename: str
    chunk_id: int
    chunk_index: int
    content_preview: str


class AskResponse(BaseModel):
    question: str
    top_k: int
    total_chunks: int
    answer: str
    sources: list[AskSource]