from sqlalchemy.orm import declarative_base
from .engine import create_db_engine

Base = declarative_base()

__all__ = [
    'Base',
    'SessionLocal', 
    'get_db',
    'get_session',
    'create_db_engine',
    'init_db'
]


def init_db():
    from .base import Base
    from .models import constantDA, flashcardDA , reviewFlashcardDA , fileFlashcardDA
    from .seed import Create_SeedData
    engine = create_db_engine()
    Base.metadata.create_all(bind=engine)
    Create_SeedData(engine)