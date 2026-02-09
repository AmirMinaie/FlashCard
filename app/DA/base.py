from sqlalchemy import Column, DateTime, Integer, MetaData
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative
from sqlalchemy.sql import func
from datetime import datetime

metadata = MetaData()


@as_declarative(metadata=metadata)
class Base:
    
    @declared_attr
    def __tablename__(cls):
        import re
        name = re.sub(r'DA$', '', cls.__name__)
        return name 
    
    id = Column(Integer, primary_key=True)
    
    createAt = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(),
        server_default=func.now(),
        doc='time of Create row'
    )
    
    updatedAt = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
        server_default=func.now(),
        doc='time Of Update row'
    )
    
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def to_dict(self, include_timestamps=True):
        result = {}
        for column in self.__table__.columns:
            if column.name == 'createdAt' and not include_timestamps:
                continue
            if column.name == 'updatedAt' and not include_timestamps:
                continue
                
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result
