from ..base import Base , validate_datetime
from sqlalchemy import Column, Float, Integer, Text , DateTime , ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates
from sqlalchemy.orm import validates
from datetime import datetime

import datetime

class reviewFlashcardDA(Base):

    flashcard_id = Column(Integer, ForeignKey("flashcard.id"), nullable=True)
    quality = Column(Integer, nullable=True)
    ease_factor = Column(Float, default=2.5 , nullable=True)
    interval = Column(Integer, default=1, nullable=True)
    repetitions = Column(Integer, default=0, nullable=True)
    review_date = Column(DateTime(timezone=True),nullable=False)
    
    flashcard = relationship(
        "flashcardDA",
        foreign_keys=[flashcard_id],
        backref="reviewFlashcard"
    )


    @validates('review_date')
    def validate_datetime(self, key, value):
        column = getattr(type(self), key, None)
        if column and hasattr(column, 'type') and isinstance(column.type, DateTime):
            if isinstance(value, str):
                return validate_datetime(value=value)
        return value