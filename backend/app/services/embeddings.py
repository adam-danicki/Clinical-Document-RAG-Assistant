from openai import OpenAI

from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)


## Service to create embeddings for text using the OpenAI API
def create_embedding(text: str) -> list[float]:
    if not text:
        raise ValueError("Text cannot be empty when creating embeddings.")
    
    respone = client.embeddings.create(
        model=settings.openai_embedding_model,
        input=text,
    )

    return respone.data[0].embedding