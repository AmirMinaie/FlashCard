from sqlalchemy.orm import sessionmaker, Session
from .engine import create_db_engine

_engine = create_db_engine()

# Session Factory
SessionLocal = sessionmaker(
    bind=_engine,
    autocommit=False,
    autoflush=False
)

def get_session() -> Session:
    db = SessionLocal()
    return db