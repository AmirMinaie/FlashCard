from ..base import Base
from .studyScheduleItemDA import studyScheduleItemDA
from .constantDA import constantDA
from sqlalchemy import ( Column, Integer, Date, ForeignKey, Text )
from sqlalchemy.orm import relationship


class studySessionDA(Base):

    schedule_item_id = Column( Integer, ForeignKey("studyScheduleItem.id"), nullable=False )
    study_date = Column(Date,nullable=False)
    start_page = Column( Integer, nullable=False )
    end_page = Column( Integer, nullable=False )
    duration_seconds = Column( Integer, nullable=True )
    note = Column( Text, nullable=True )

    schedule_item = relationship( "studyScheduleItemDA", foreign_keys=[schedule_item_id], backref="study_sessions", lazy="joined" )

    @property
    def completedPages(self):
        if self.start_page is None or self.end_page is None:
            return 0

        return max(self.end_page - self.start_page + 1,0)