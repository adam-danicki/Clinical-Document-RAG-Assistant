from pydantic_settings import BaseSettings
from pydantic import BaseModel


class Settings(BaseSettings):
    database_url: str

    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-5.4-mini"

    class Config:
        env_file = ".env"


settings = Settings()