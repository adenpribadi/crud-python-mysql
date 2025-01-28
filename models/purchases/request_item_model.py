# models/purchases/request_item_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Numeric, event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models import Base

class PurchaseRequestItem(Base):
    __tablename__ = 'purchase_request_items'

    id = Column(Integer, primary_key=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    outstanding = Column(Numeric(10, 2), nullable=False, default=0)
    remarks = Column(String(255))
    status = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relasi dengan PurchaseRequest
    purchase_request_id = Column(Integer, ForeignKey('purchase_requests.id'), nullable=False)
    material_id = Column(Integer, ForeignKey('materials.id'), nullable=True)
    general_id = Column(Integer, ForeignKey('generals.id'), nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    updated_by = Column(Integer, ForeignKey('users.id'))

    # belongs_to
    purchase_request = relationship('PurchaseRequest', back_populates='request_items', lazy=True)
    material = relationship('Material', back_populates='request_items', lazy=True)
    general = relationship('General', back_populates='request_items', lazy=True)
    created_user = relationship('User', foreign_keys=[created_by])
    updated_user = relationship('User', foreign_keys=[updated_by])

# Event Listener untuk memastikan nomor referensi di-generate sebelum insert
@event.listens_for(PurchaseRequestItem, 'before_insert')
def before_insert(mapper, connection, target):
    if target.outstanding is None:
        target.outstanding = target.quantity  # Misalnya outstanding di-set ke jumlah quantity