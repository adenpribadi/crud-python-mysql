# unit_model.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from . import Base

class Unit(Base):
    __tablename__ = 'units'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    materials = relationship('Material', back_populates='unit')
    generals = relationship('General', back_populates='unit')
