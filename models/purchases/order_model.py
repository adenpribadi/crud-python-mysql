# models/purchases/order_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Text, event
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from models import Base
from models import EmployeeSection, Department  # Pastikan model diimpor dengan benar

import calendar
from datetime import datetime


class PurchaseOrder(Base):
    __tablename__ = 'purchase_orders'

    id = Column(Integer, primary_key=True)
    reference_number = Column(String, nullable=False, unique=True)
    reference_date = Column(Date, default=func.now(), nullable=False)
    kind = Column(Text)
    remarks = Column(Text)
    top_days = Column(Text)
    status = Column(Text)
    outstanding = Column(Integer)

    department_id = Column(Integer, ForeignKey('departments.id'))
    employee_section_id = Column(Integer, ForeignKey('employee_sections.id'))
    contact_id = Column(Integer, ForeignKey('contacts.id'))
    currency_id = Column(Integer, ForeignKey('currencies.id'))
    tax_id = Column(Integer, ForeignKey('taxes.id'))
    term_of_payment_id = Column(Integer, ForeignKey('term_of_payments.id'))

    created_by = Column(Integer, ForeignKey('users.id'))
    updated_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # New attributes for approval and cancellation tracking
    approved1_at = Column(DateTime, nullable=True)
    approved1_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved2_at = Column(DateTime, nullable=True)
    approved2_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved3_at = Column(DateTime, nullable=True)
    approved3_by = Column(Integer, ForeignKey('users.id'), nullable=True)

    canceled1_at = Column(DateTime, nullable=True)
    canceled1_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    canceled2_at = Column(DateTime, nullable=True)
    canceled2_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    canceled3_at = Column(DateTime, nullable=True)
    canceled3_by = Column(Integer, ForeignKey('users.id'), nullable=True)

    # belongs_to
    department = relationship('Department', back_populates='purchase_orders')
    employee_section = relationship('EmployeeSection', back_populates='purchase_orders')
    contact = relationship('Contact', back_populates='purchase_orders')
    currency = relationship('Currency', back_populates='purchase_orders')
    tax = relationship('Tax', back_populates='purchase_orders')
    term_of_payment = relationship('TermOfPayment', back_populates='purchase_orders')

    # Relationship hanya di model PurchaseOrder
    created_user = relationship('User', foreign_keys=[created_by])
    updated_user = relationship('User', foreign_keys=[updated_by])

    approved1_user = relationship("User", foreign_keys=[approved1_by])
    approved2_user = relationship("User", foreign_keys=[approved2_by])
    approved3_user = relationship("User", foreign_keys=[approved3_by])
    canceled1_user = relationship("User", foreign_keys=[canceled1_by])
    canceled2_user = relationship("User", foreign_keys=[canceled2_by])
    canceled3_user = relationship("User", foreign_keys=[canceled3_by])
    
    # has_many
    order_items = relationship('PurchaseOrderItem', back_populates='purchase_order', lazy=True)

    @property
    def reference_date_min(self):
        if self.reference_date:
            return self.reference_date.replace(day=1)
        return datetime.today().replace(day=1)

    @property
    def reference_date_max(self):
        if self.reference_date:
            _, last_day = calendar.monthrange(self.reference_date.year, self.reference_date.month)
            return self.reference_date.replace(day=last_day)
        today = datetime.today()
        _, last_day = calendar.monthrange(today.year, today.month)
        return today.replace(day=last_day)

    def generate_reference_number(self, session: Session):
        """Generate nomor referensi berdasarkan bulan dan urutan"""
        begin_date = self.reference_date.replace(day=1)
        _, last_day = calendar.monthrange(self.reference_date.year, self.reference_date.month)
        end_date = self.reference_date.replace(day=last_day)

        # Menggunakan session untuk query
        last_record = session.query(PurchaseOrder).filter(
            PurchaseOrder.reference_date >= begin_date,
            PurchaseOrder.reference_date <= end_date
        ).order_by(PurchaseOrder.reference_number.desc()).first()  # Menggunakan first() untuk mendapatkan satu record
        
        base_number = f"PO/{begin_date.strftime('%y/%m/')}"

        # Menentukan nomor urut berdasarkan record terakhir
        if last_record:
            last_reference_number = last_record.reference_number
            last_number = int(last_reference_number[-4:])
            new_number = last_number + 1
        else:
            new_number = 1

        seq = f"{new_number:04d}"  # Format nomor urut 4 digit
        self.reference_number = f"{base_number}{seq}"



# Event Listener untuk memastikan nomor referensi di-generate sebelum insert
@event.listens_for(PurchaseOrder, 'before_insert')
def before_insert(mapper, connection, target):
    if not target.reference_number:
        # Pastikan session dipass ke generate_reference_number
        session = Session.object_session(target)  # Ambil session terkait target
        target.generate_reference_number(session)
