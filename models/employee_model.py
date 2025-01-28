# employee_model.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base
from .position_model import Position  # Pastikan diimpor di sini
from .work_status_model import WorkStatus  # Pastikan diimpor di sini

class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    image = Column(String)
    nik = Column(String)
    name = Column(String)
    join_date = Column(Date)
    born_date = Column(Date)
    born_place = Column(String)
    gender = Column(String)
    phone_number = Column(String)
    email_address = Column(String)
    
    image = Column(String)

    department_id = Column(Integer, ForeignKey('departments.id'))
    position_id = Column(Integer, ForeignKey('positions.id'))
    work_status_id = Column(Integer, ForeignKey('employee_work_statuses.id'))
    
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=func.now())
    updated_by = Column(Integer, ForeignKey('users.id'))
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    department = relationship('Department', back_populates='employees')
    position = relationship('Position', back_populates='employees')  # Pastikan relasi menggunakan 'Position'
    work_status = relationship('WorkStatus', back_populates='employees')

