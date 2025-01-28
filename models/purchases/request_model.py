# models/purchases/request_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Text, event
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from models import Base
from models import EmployeeSection, Department  # Pastikan model diimpor dengan benar

import calendar
from datetime import datetime


class PurchaseRequest(Base):
    __tablename__ = 'purchase_requests'

    id = Column(Integer, primary_key=True)
    reference_number = Column(String, nullable=False, unique=True)
    reference_date = Column(Date, default=func.now(), nullable=False)
    request_kind = Column(Text)
    remarks = Column(Text)
    status = Column(Text)
    outstanding = Column(Integer)

    department_id = Column(Integer, ForeignKey('departments.id'))
    employee_section_id = Column(Integer, ForeignKey('employee_sections.id'))
    created_by = Column(Integer, ForeignKey('users.id'))
    updated_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # belongs_to
    department = relationship('Department', back_populates='purchase_requests')
    employee_section = relationship('EmployeeSection', back_populates='purchase_requests')

    # Relationship hanya di model PurchaseRequest
    created_user = relationship('User', foreign_keys=[created_by])
    updated_user = relationship('User', foreign_keys=[updated_by])

    # has_many
    request_items = relationship('PurchaseRequestItem', back_populates='purchase_request', lazy=True)

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
        last_record = session.query(PurchaseRequest).filter(
            PurchaseRequest.department_id == self.department_id,
            PurchaseRequest.employee_section_id == self.employee_section_id,
            PurchaseRequest.reference_date >= begin_date,
            PurchaseRequest.reference_date <= end_date
        ).order_by(PurchaseRequest.reference_number.desc()).first()  # Menggunakan first() untuk mendapatkan satu record

        section_code = "DEFAULT"
        # Query untuk memastikan relasi EmployeeSection ter-load
        section = session.query(EmployeeSection).filter_by(id=self.employee_section_id).one_or_none()
        if section:
            # Query untuk memastikan relasi Department ter-load dari EmployeeSection
            department = session.query(Department).filter_by(id=section.department_id).one_or_none()
            if department:
                section_code = f"{department.code}{section.code}"
        elif self.department_id:
            # Query untuk memastikan Department ter-load langsung dari PurchaseRequest
            department = session.query(Department).filter_by(id=self.department_id).one_or_none()
            if department:
                section_code = f"{department.code}A"
        
        base_number = f"PRF/{section_code}/{begin_date.strftime('%y/%m/')}"

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
@event.listens_for(PurchaseRequest, 'before_insert')
def before_insert(mapper, connection, target):
    if not target.reference_number:
        # Pastikan session dipass ke generate_reference_number
        session = Session.object_session(target)  # Ambil session terkait target
        target.generate_reference_number(session)
