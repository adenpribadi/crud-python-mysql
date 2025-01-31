# department_model.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from . import Base

class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String)

    employees = relationship("Employee", back_populates="department")
    employee_sections = relationship("EmployeeSection", back_populates="department")
    purchase_requests = relationship('PurchaseRequest', back_populates='department')
    purchase_orders = relationship('PurchaseOrder', back_populates='department')
