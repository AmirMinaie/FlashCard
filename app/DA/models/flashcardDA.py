from ..base import Base
from sqlalchemy import Column, Integer, Text , DateTime , ForeignKey , Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import datetime

class flashcardDA(Base):

    title = Column(Text, nullable=False)
    definition = Column(Text, nullable=False)
    example = Column(Text, nullable=False)
    collocation = Column(Text, nullable=False)
    pastParticiple = Column(Text, nullable=False)
    pastTense = Column(Text, nullable=False)
    pronunciation = Column(Text, nullable=False)
    pos_id = Column(Integer, ForeignKey("constant.id"), nullable=True)
    type_id = Column(Integer, ForeignKey("constant.id"), nullable=True)
    box_id  = Column(Integer, ForeignKey("constant.id"), nullable=True)
    level_id = Column(Integer, ForeignKey("constant.id"), nullable=True)

    type_ = relationship(
        "constantDA",
        foreign_keys=[type_id],
        backref="type_flashcards", 
        lazy='joined'
    )

    box = relationship(
        "constantDA",
        foreign_keys=[box_id],
        backref="box_flashcards", 
        lazy='joined'
    )

    pos = relationship(
        "constantDA",
        foreign_keys=[pos_id],
        backref="pos_flashcards", 
        lazy='joined'
    )

    level = relationship(
        "constantDA",
        foreign_keys=[level_id],
        backref="level_flashcards", 
        lazy='joined'
    )

    __table_args__ = (
        Index('idx_unique_title', 'title', unique=True),
    )

    files = relationship("fileFlashcardDA", 
                         back_populates="flashcard",
                         cascade="all, delete-orphan")

    reviews = relationship("reviewFlashcardDA",
                            back_populates="flashcard",
                            order_by= "desc(reviewFlashcardDA.review_date)",
                            lazy= 'dynamic'
                        )
    @property
    def last_review(self):
        if self.reviews:
            return self.reviews[0]
        return None
    
    @hybrid_property
    def last_review_date(self):
        """تاریخ آخرین review (برای استفاده در Python)"""
        if self.reviews:
            return self.reviews[0].review_date
        return None