from ..base import Base
from sqlalchemy import Column, Integer, Text , DateTime , ForeignKey
from sqlalchemy.orm import relationship
import datetime

class reviewFlashcardDA(Base):

    flashcard_id = Column(Integer, ForeignKey("flashcard.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("constant.id"), nullable=True)
    box_id = Column(Integer, ForeignKey("constant.id"), nullable=True)
    
    flashcard = relationship(
        "flashcardDA",
        foreign_keys=[flashcard_id],
        backref="reviewFlashcard"
    )

    status = relationship(
        "constantDA",
        foreign_keys=[status_id],
        backref="status_reviewFlashcard"
    )

    box = relationship(
        "constantDA",
        foreign_keys=[box_id],
        backref="Box_reviewFlashcard"
    )
