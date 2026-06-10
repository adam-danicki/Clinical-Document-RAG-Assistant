# Clinical Document RAG Assistant

Clinical Document RAG Assistant is a FastAPI + PostgreSQL/pgvector backend for uploading PDF documents, extracting text, chunking content, generating embeddings, and answering questions using retrieval-augmented generation (RAG).

The project is currently backend-only. It supports document ingestion, semantic search over uploaded PDFs, and source-grounded LLM answers through OpenAI.

The goal is to build a production-style clinical/healthcare document assistant that demonstrates backend API design, document processing, vector search, database storage, and LLM integration without being just a simple chatbot.



## What this project does

- Uploads PDF documents through a FastAPI endpoint
- Saves uploaded files locally
- Extracts text from PDFs
- Splits extracted text into overlapping chunks
- Stores document metadata and chunks in PostgreSQL
- Generates OpenAI embeddings for each chunk
- Stores embeddings using PostgreSQL + pgvector
- Performs semantic search over document chunks
- Generates source-grounded answers using retrieved chunks
- Returns citations/source previews with answers
- Provides OpenAPI docs through FastAPI Swagger UI



## Current status

This project currently includes the backend RAG pipeline.

Completed so far:

- FastAPI backend setup
- Modular API/service structure
- PDF upload endpoint
- PDF parsing service
- Text chunking service
- PostgreSQL database connection
- SQLAlchemy models for documents and chunks
- pgvector extension setup
- Embedding column for document chunks
- OpenAI embedding service
- Semantic search endpoint
- RAG answer-generation endpoint
- Source-backed response format

Not built yet:

- React frontend (scaffolded in `frontend/`)
- Authentication
- User accounts
- Document deletion endpoint
- Alembic migrations
- Automated tests
- Deployment
- Admin dashboard



## Tech stack

- Python 3.13 currently used locally
- FastAPI
- Uvicorn
- SQLAlchemy ORM
- PostgreSQL
- pgvector
- Docker / Docker Compose
- OpenAI API
- pypdf
- Pydantic / pydantic-settings



## Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── documents.py          # Document upload, listing, search, and ask endpoints
│   │   ├── services/
│   │   │   ├── pdf_parser.py         # Extracts text from uploaded PDFs
│   │   │   ├── chunker.py            # Splits extracted text into overlapping chunks
│   │   │   ├── embeddings.py         # Creates OpenAI embeddings for text chunks/questions
│   │   │   └── rag.py                # Generates source-grounded answers from retrieved chunks
│   │   ├── uploads/                  # Local storage for uploaded PDF files
│   │   ├── config.py                 # Environment variable settings
│   │   ├── database.py               # SQLAlchemy engine/session setup
│   │   ├── main.py                   # FastAPI app entrypoint
│   │   ├── models.py                 # SQLAlchemy models for documents and chunks
│   │   └── schemas.py                # Pydantic request schemas
│   ├── .env                          # Local environment variables (DO NOT commit)
│   └── requirements.txt              # Python dependencies
├── docker-compose.yml                # Local PostgreSQL + pgvector service
├── .gitignore
└── README.md
```



## Data model

### Document

Represents one uploaded PDF.

Fields:

- `id`
- `filename`
- `content_type`
- `file_path`
- `text_length`
- `chunk_count`
- `uploaded_at`

### DocumentChunk

Represents one chunk of extracted document text.

Fields:

- `id`
- `document_id`
- `chunk_index`
- `content`
- `embedding`

### Relationships

- One Document has many DocumentChunks
- Each DocumentChunk belongs to one Document

Relationship:

```text
Document → many DocumentChunks
```

The `document_id` field in `document_chunks` is a foreign key pointing to `documents.id`.

This allows the system to trace every retrieved chunk back to the original uploaded PDF.



## RAG pipeline

The backend currently follows this pipeline:

```text
PDF upload
→ save file locally
→ extract text with pypdf
→ split text into chunks
→ create OpenAI embeddings
→ store chunks + embeddings in PostgreSQL/pgvector
→ embed user question
→ retrieve closest chunks using vector similarity
→ generate answer using retrieved sources
→ return answer + source previews
```

This is the core retrieval-augmented generation flow.

The system does not fine-tune a model. Instead, it uses RAG so answers are grounded in uploaded documents.



## API Overview

OpenAPI / Swagger UI:

```text
http://127.0.0.1:8000/docs
```

### Health / metadata

```text
GET /
```

Returns a basic message confirming the backend is running.

```text
GET /health
```

Returns backend health status.

```text
GET /version
```

Returns project version information.



## Document endpoints

### List uploaded documents

```text
GET /documents/
```

Returns stored document metadata from PostgreSQL.

Example response:

```json
{
  "documents": [
    {
      "id": 1,
      "filename": "policy.pdf",
      "content_type": "application/pdf",
      "file_path": "app/uploads/policy.pdf",
      "text_length": 8420,
      "chunk_count": 9,
      "uploaded_at": "2026-05-26T..."
    }
  ]
}
```



### Document service status

```text
GET /documents/status
```

Returns:

```json
{
  "document_service": "ready"
}
```



### Upload PDF

```text
POST /documents/upload
```

Accepts a PDF file through multipart form data.

Current behavior:

- Validates that the file is a PDF
- Saves the file locally
- Extracts text
- Splits text into chunks
- Creates embeddings for each chunk
- Saves document metadata and chunks to PostgreSQL
- Returns upload/chunking/embedding summary

Example response:

```json
{
  "message": "File uploaded, parsed, chunked, embedded, and saved successfully",
  "document_id": 1,
  "filename": "Adam_Danicki_Transcript.pdf",
  "content_type": "application/pdf",
  "file_path": "app/uploads/Adam_Danicki_Transcript.pdf",
  "text_length": 7120,
  "chunk_count": 9,
  "embeddings_created": 9,
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "first_chunk_preview": "Print Date: 05/14/2026..."
}
```



## Search endpoint

### Semantic search over document chunks

```text
POST /documents/search
```

Request body:

```json
{
  "question": "What machine learning course did this student take?",
  "top_k": 5
}
```

What it does:

- Creates an embedding for the question
- Compares it against stored chunk embeddings using pgvector
- Returns the most semantically relevant chunks

Example response:

```json
{
  "question": "What machine learning course did this student take?",
  "top_k": 5,
  "results": [
    {
      "document_id": 1,
      "filename": "Adam_Danicki_Transcript.pdf",
      "chunk_id": 7,
      "chunk_index": 6,
      "content_preview": "COMPSCI 589 Machine Learning..."
    }
  ]
}
```



## Ask endpoint

### Ask a source-grounded question

```text
POST /documents/ask
```

Request body:

```json
{
  "question": "What classes did this student take?",
  "top_k": 5
}
```

What it does:

- Embeds the user question
- Retrieves the top matching document chunks
- Sends the retrieved chunks to the LLM
- Generates an answer using only the retrieved context
- Returns the answer and source previews

Example response:

```json
{
  "question": "What classes did this student take?",
  "answer": "The transcript shows the student took several courses, including COMPSCI 589 Machine Learning, COMPSCI 528 Mobile and Ubiquitous Computing, COMPSCI 453 Computer Networks, and others [Source 1].",
  "sources": [
    {
      "source_number": 1,
      "document_id": 1,
      "filename": "Adam_Danicki_Transcript.pdf",
      "chunk_id": 7,
      "chunk_index": 6,
      "content_preview": "BIOLOGY 152 Introductory Biology II..."
    }
  ]
}
```



## Environment variables

Create a `.env` file inside the `backend/` directory.

```env
DATABASE_URL=postgresql://clinical_user:clinical_password@localhost:5432/clinical_rag
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=your_chat_model_here
```

Do not commit `.env` to GitHub.



## Running locally

### 1. Start PostgreSQL with Docker

From the project root:

```bash
docker compose up -d
```

Check that the container is running:

```bash
docker ps
```

You should see:

```text
clinical_rag_db
```



### 2. Set up the backend environment

From the `backend/` directory:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```



### 3. Enable pgvector

Connect to the `clinical_rag` database and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

If the database was created before the embedding column was added, run:

```sql
ALTER TABLE document_chunks
ADD COLUMN IF NOT EXISTS embedding vector(1536);
```

For a fresh database, the SQLAlchemy model should create the embedding column automatically, assuming the pgvector extension is enabled first.



### 4. Run the backend

From the `backend/` directory:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```



## Useful SQL checks

Check tables:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';
```

Check document rows:

```sql
SELECT * FROM documents;
```

Check chunk rows:

```sql
SELECT 
    id,
    document_id,
    chunk_index,
    LEFT(content, 100) AS preview,
    embedding IS NOT NULL AS has_embedding
FROM document_chunks
ORDER BY id DESC
LIMIT 10;
```

Check embedding dimensions:

```sql
SELECT 
    id,
    chunk_index,
    vector_dims(embedding) AS dimensions
FROM document_chunks
WHERE embedding IS NOT NULL
ORDER BY id DESC
LIMIT 10;
```



## Current limitations

- No frontend yet
- No authentication or user management yet
- Uploaded files are stored locally
- No duplicate-file prevention yet
- No document deletion endpoint yet
- No Alembic migrations yet
- No automated tests yet
- No OCR support for scanned PDFs
- No production deployment yet
- Existing databases may need manual SQL updates until migrations are added



## Planned improvements

- Add React frontend
- Add document detail page
- Add document deletion endpoint
- Add source citation display in the UI
- Add authentication and user-specific documents
- Add Alembic migrations
- Add pytest API tests
- Add GitHub Actions CI
- Add Dockerfile for the backend
- Add deployed demo
- Add OCR fallback for scanned PDFs
- Add document comparison feature
- Add retrieval evaluation tests
- Add better prompt controls for clinical/policy-style answers



## Resume summary

Clinical Document RAG Assistant is a backend RAG system that demonstrates:

- REST API design with FastAPI
- PDF upload and parsing
- Text chunking and document ingestion
- PostgreSQL database design
- pgvector semantic search
- OpenAI embeddings
- Source-grounded LLM answer generation
- Modular backend architecture
- Docker-based local development

This project is intended to grow into a full-stack clinical document assistant for healthcare policy search and source-backed question answering.
