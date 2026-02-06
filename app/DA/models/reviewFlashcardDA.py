from ..base import Base
from sqlalchemy import Column, Float, Integer, Text , DateTime , ForeignKey
from sqlalchemy.orm import relationship
import datetime

class reviewFlashcardDA(Base):

    flashcard_id = Column(Integer, ForeignKey("flashcard.id"), nullable=True)
    quality = Column(Integer, nullable=True)
    box_id = Column(Integer, ForeignKey("constant.id"), nullable=True)
    ease_factor = Column(Float, default=2.5 , nullable=True)
    interval = Column(Integer, default=1, nullable=True)
    repetitions = Column(Integer, default=0, nullable=True)
    review_date = Column(DateTime(timezone=True),nullable=False)
    
    flashcard = relationship(
        "flashcardDA",
        foreign_keys=[flashcard_id],
        backref="reviewFlashcard"
    )

    box = relationship(
        "constantDA",
        foreign_keys=[box_id],
        backref="Box_reviewFlashcard"
    )
