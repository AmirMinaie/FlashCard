from ..base import Base
from sqlalchemy import Column, Integer, Text , Index

class constantDA(Base):
    name = Column(Text, nullable=False)
    caption = Column(Text, nullable=False)
    type = Column(Text, nullable=False)

    __table_args__ = (
        Index('idx_unique_Name', 'name', unique=True),
    )
