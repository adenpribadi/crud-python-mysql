from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base

class TermOfPayment(Base):
    __tablename__ = 'term_of_payments'

    id = Column(Integer, primary_key=True)
    name = Column(String(24))
    code = Column(String(8))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # has_many
    purchase_orders = relationship('PurchaseOrder', back_populates='term_of_payment', lazy=True)