from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from db import Base
from sqlalchemy.dialects.postgresql import ARRAY

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    designation = Column(String)
    role = Column(String(50))  # employee, teamlead, manager, hr
    department = Column(String)
    manager_id = Column(Integer, ForeignKey('employees.id'))

class Timesheet(Base):
    __tablename__ = "timesheets"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    date = Column(Date)
    project = Column(String)
    hours = Column(Float)
    description = Column(String)
    status = Column(String, default="draft")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    name = Column(String)
    client = Column(String)
    allocation_pct = Column(Integer)

class Holiday(Base):
    __tablename__ = "holidays"
    
    date = Column(Date, primary_key=True)
    name = Column(String)
    type = Column(String)
