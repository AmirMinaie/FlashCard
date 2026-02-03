from ..base import Base
from sqlalchemy import Column, Integer, Text , DateTime , ForeignKey , Index
from sqlalchemy.orm import relationship
import datetime

class fileFlashcardDA(Base):

    flashcard_id = Column(Integer, ForeignKey("flashcard.id"), nullable=True)
    file_path = Column(Text, default=datetime.datetime.utcnow)
    type_id = Column(Integer, ForeignKey("constant.id"), nullable=True)
    
    flashcard = relationship(
        "flashcardDA",
        foreign_keys=[flashcard_id],
        backref="fileFlashcard"
    )

    type = relationship(
        "constantDA",
        foreign_keys=[type_id],
        backref="type_fileFlashcard"
    )
