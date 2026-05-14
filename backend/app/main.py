from fastapi import FastAPI
from app.api.documents import router as documents_router

app = FastAPI()
app.include_router(documents_router)

@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get('/version')
def version():
    return {
        "version": "0.1.0",
        "project": "Clinical Document RAG Assistant"
    }