from ..base import Base
from .reviewFlashcardDA import reviewFlashcardDA
from sqlalchemy import Column, Integer, Text , DateTime , ForeignKey , Index , desc
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func
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
        lazy='joined')

    box = relationship(
        "constantDA",
        foreign_keys=[box_id],
        backref="box_flashcards", 
        lazy='joined')

    pos = relationship(
        "constantDA",
        foreign_keys=[pos_id],
        backref="pos_flashcards", 
        lazy='joined')

    level = relationship(
        "constantDA",
        foreign_keys=[level_id],
        backref="level_flashcards", 
        lazy='joined')

    __table_args__ = (
        Index('idx_unique_title', 'title', unique=True),
    )

    files = relationship("fileFlashcardDA",
                         foreign_keys="[fileFlashcardDA.flashcard_id]",
                         cascade="all, delete-orphan",
                         overlaps="fileFlashcard",
                         back_populates="flashcard",
                        )

    reviews = relationship(
        reviewFlashcardDA,
        foreign_keys=[reviewFlashcardDA.flashcard_id], 
        order_by=reviewFlashcardDA.review_date.desc(),
        lazy='joined',
        overlaps="reviewFlashcard"
    )

    @property
    def last_review(self):
        if self.reviews:
            return self.reviews[0]
        return None
    
    @hybrid_property
    def last_review_date(self):
        """تاریخ رویو بعدی (برای استفاده در Python)"""
        if self.reviews:
            return self.reviews[0].review_date
        return None
    
    @last_review_date.expression
    def last_review_date(cls):
        """ "تاریخ رویو بعدی"""
        # این expression برای استفاده در query
        return select(func.max(reviewFlashcardDA.review_date))\
            .where(reviewFlashcardDA.flashcard_id == cls.id)\
            .correlate(cls)\
            .scalar_subquery()
    

    @hybrid_property
    def last_reviewed_date(self):
        """ تاریخ آخرین رویو (برای استفاده در Python)"""
        if self.reviews:
            return self.reviews[0].createAt
        return None
    
    @last_review_date.expression
    def last_reviewed_date(cls):
        # این expression برای استفاده در query
        return select(func.max(reviewFlashcardDA.createAt))\
            .where(reviewFlashcardDA.flashcard_id == cls.id)\
            .correlate(cls)\
            .scalar_subquery()