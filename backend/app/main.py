from fastapi import FastAPI
from app.api.documents import router as documents_router

### Main FastAPI application
app = FastAPI()
app.include_router(documents_router)

## Basic endpoints for health checks and version info
@app.get("/")
def root():
    return {"message": "Backend is running"}

## Additional endpoints for health checks
@app.get("/health")
def health_check():
    return {"status": "healthy"}

## Endpoint to provide version information about the backend
@app.get('/version')
def version():
    return {
        "version": "0.1.0",
        "project": "Clinical Document RAG Assistant"
    }