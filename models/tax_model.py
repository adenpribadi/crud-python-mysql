from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base

class Tax(Base):
    __tablename__ = 'taxes'

    id = Column(Integer, primary_key=True)
    name = Column(String(16))
    value = Column(Float)
    status = Column(Enum('active','suspend'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # has_many
    purchase_orders = relationship('PurchaseOrder', back_populates='tax', lazy=True)