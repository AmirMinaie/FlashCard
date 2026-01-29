from ..base import Base
from sqlalchemy import Column, Integer, Text , DateTime , ForeignKey , Index
from sqlalchemy.orm import relationship
import datetime

class flashcardDA(Base):
    __tablename__ = "flashcard"

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    definition = Column(Text, nullable=False)
    example = Column(Text, nullable=False)
    collocation = Column(Text, nullable=False)
    pastParticiple = Column(Text, nullable=False)
    pastTense = Column(Text, nullable=False)
    pronunciation = Column(Text, nullable=False)
    pos_id = Column(Integer, ForeignKey("constant.id"), nullable=True)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)
    type_id = Column(Integer, ForeignKey("constant.id"), nullable=True)
    box_id  = Column(Integer, ForeignKey("constant.id"), nullable=True)
    level_id = Column(Integer, ForeignKey("constant.id"), nullable=True)

    type_ = relationship(
        "constantDA",
        foreign_keys=[type_id],
        backref="type_flashcards"
    )

    box = relationship(
        "constantDA",
        foreign_keys=[box_id],
        backref="box_flashcards"
    )

    pos = relationship(
        "constantDA",
        foreign_keys=[pos_id],
        backref="pos_flashcards"
    )

    level = relationship(
        "constantDA",
        foreign_keys=[level_id],
        backref="level_flashcards"
    )

    __table_args__ = (
        Index('idx_unique_title', 'title', unique=True),
    )