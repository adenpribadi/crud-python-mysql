# work_status_model.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from . import Base

class WorkStatus(Base):
    __tablename__ = 'employee_work_statuses'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    employees = relationship("Employee", back_populates="work_status")
