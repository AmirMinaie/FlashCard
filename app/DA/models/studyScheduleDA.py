from ..base import *
from .constantDA import constantDA
from sqlalchemy.orm import validates
from sqlalchemy import (Column,Integer,Text,Date,ForeignKey)
from sqlalchemy.orm import relationship


class studyScheduleDA(Base):

    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status_id = Column( Integer, ForeignKey("constant.id"), nullable=False )
    status = relationship( "constantDA", foreign_keys=[status_id], backref="schedule_statuses", lazy="joined" )
    items = relationship( "studyScheduleItemDA", foreign_keys="[studyScheduleItemDA.schedule_id]", cascade="all, delete-orphan", back_populates="schedule" )

    @validates('start_date', 'end_date')
    def validate_date(self, key, value):
        column = getattr(type(self), key, None)
    
        if column and hasattr(column, 'type') and isinstance(column.type, Date):
            if isinstance(value, str):
                return validate_datetime(value=value).date()
    
        return value