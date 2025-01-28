# employee_section_model.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base

class EmployeeSection(Base):
    __tablename__ = 'employee_sections'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)

    department_id = Column(Integer, ForeignKey('departments.id'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # belongs_to
    department = relationship('Department', back_populates='employee_sections')

    # has_many
    purchase_requests = relationship('PurchaseRequest', back_populates='employee_section')