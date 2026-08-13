from ..base import Base
from .constantDA import constantDA
from sqlalchemy import ( Column, Integer, ForeignKey, Index )
from sqlalchemy.orm import relationship


class studyScheduleItemDA(Base):

    schedule_id = Column( Integer, ForeignKey("studySchedule.id"), nullable=False )
    book_id = Column( Integer, ForeignKey("book.id"), nullable=False )
    weekday_id = Column( Integer, ForeignKey("constant.id"), nullable=False )
    pages = Column( Integer, nullable=False )
    schedule = relationship( "studyScheduleDA", foreign_keys=[schedule_id], back_populates="items" )
    book = relationship( "bookDA", foreign_keys=[book_id], backref="schedule_items", lazy="joined" )
    weekday = relationship( "constantDA", foreign_keys=[weekday_id], backref="study_schedule_items", lazy="joined" )

    __table_args__ = (
        Index(
            "idx_schedule_item_schedule_weekday_book",
            "schedule_id",
            "weekday_id",
            "book_id",
            unique=True
        ),
    )