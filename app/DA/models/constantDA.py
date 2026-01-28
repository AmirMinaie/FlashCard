from ..base import Base
from sqlalchemy import Column, Integer, Text

class constantDA(Base):
    __tablename__ = "constant"
    id = Column(Integer, primary_key=True)
    Name = Column(Text, nullable=False)
    Caption = Column(Text, nullable=False)
    Type = Column(Text, nullable=False)
