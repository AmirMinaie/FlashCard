from ..base import Base
from sqlalchemy import Column, Integer, Text , DateTime , ForeignKey
from sqlalchemy.orm import relationship
import datetime

class flashcardDA(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    example = Column(Text, nullable=False)

    type_Id = Column(Integer, ForeignKey("constant.id"), nullable=True)
    box_Id  = Column(Integer, ForeignKey("constant.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    type_ = relationship(
        "constantDA",
        foreign_keys=[type_Id],
        backref="type_flashcards"
    )

    box_ = relationship(
        "constantDA",
        foreign_keys=[box_Id],
        backref="box_flashcards"
    )
