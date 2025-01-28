from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.sql import func
from . import Base

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(126))
    internal_reference = Column(String(126))
    status = Column(Enum('active','suspend'))
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=func.now())
    updated_by = Column(Integer, ForeignKey('users.id'))
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

