from sqlalchemy.orm import sessionmaker, Session
from . import engine

# Session Factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

def get_session() -> Session:
    return SessionLocal()
