from ..base import *
from .constantDA import constantDA
from sqlalchemy.orm import validates
from sqlalchemy import Column, Integer, Text, Date, ForeignKey, Index
from sqlalchemy.orm import relationship


class bookDA(Base):

    title = Column(Text, nullable=False)
    author = Column(Text, nullable=True)
    total_pages = Column(Integer, nullable=False)
    current_page = Column(Integer, nullable=False, default=0)
    start_date = Column(Date, nullable=True)
    status_id = Column( Integer, ForeignKey("constant.id"), nullable=True )
    status = relationship( "constantDA", foreign_keys=[status_id], backref="BookStatus", lazy="joined" )

    __table_args__ = (Index("idx_unique_book_title", "title", unique=True),)

    @validates('start_date')
    def validate_careatAt(self, key, value):
        column = getattr(type(self), key, None)
        if column and hasattr(column, 'type') and isinstance(column.type, DateTime):
            if isinstance(value, str):
                return validate_datetime(value=value)
        return value