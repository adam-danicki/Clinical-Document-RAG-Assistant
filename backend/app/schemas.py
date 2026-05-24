from openai import BaseModel


## Pydantic models for request validation in API endpoints
class SearchRequest(BaseModel):
    question: str
    top_k: int = 5


## New Pydantic model for the /ask endpoint
class AskRequest(BaseModel):
    question: str
    top_k: int = 5