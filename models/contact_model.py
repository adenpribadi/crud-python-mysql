from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    business_associate = Column(String(255))
    contact_type = Column(String(255))
    status = Column(Enum('active','suspend'))
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=func.now())
    updated_by = Column(Integer, ForeignKey('users.id'))
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # has_many
    purchase_orders = relationship('PurchaseOrder', back_populates='contact', lazy=True)