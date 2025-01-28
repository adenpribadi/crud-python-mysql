# position_model.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from . import Base

class Position(Base):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    employees = relationship('Employee', back_populates='position')
