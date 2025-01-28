# material_model.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class Material(Base):
    __tablename__ = 'materials'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    internal_reference = Column(String)
    unit_id = Column(Integer, ForeignKey('units.id')) 

    # belongs_to
    unit = relationship('Unit', back_populates='materials')

    # has_many
    request_items = relationship('PurchaseRequestItem', back_populates='material', lazy=True)
