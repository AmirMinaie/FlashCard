from ..base import Base
from sqlalchemy import Column, Integer, Text ,String, DateTime , ForeignKey , Index
from sqlalchemy.orm import relationship
import datetime

class fileFlashcardDA(Base):

    flashcard_id = Column(Integer, ForeignKey("flashcard.id"), nullable=True)
    filePath = Column(Text, default=datetime.datetime.utcnow)
    fileName = Column(String(200))
    fileSize = Column(Integer)
    type_id = Column(Integer, ForeignKey("constant.id"), nullable=True)
    sourceType_id = Column(Integer, ForeignKey("constant.id"), nullable=True)
    
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

    sourceType = relationship(
        "constantDA",
        foreign_keys=[type_id],
        backref="sourceType_fileFlashcard"
    )