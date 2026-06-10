from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)

# Enable pgvector extension
with engine.connect() as connection:
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    connection.commit()

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
