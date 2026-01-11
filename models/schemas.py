from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class UserContext(BaseModel):
    id: int
    name: str
    role: str  
    team_id: Optional[int] = None


class ChatRequest(BaseModel):
    message: str
    user_id: int


class TimesheetEntry(BaseModel):
    date: date
    hours: float


class TimesheetResponse(BaseModel):
    user_id: int
    user_name: str
    entries: List[TimesheetEntry]


class TeamMemberProject(BaseModel):
    user_id: int
    user_name: str
    project_name: str


class HolidayItem(BaseModel):
    date: date
    name: str


class GenericMessage(BaseModel):
    message: str


from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  
    team_id = Column(Integer, nullable=True)


class Timesheet(Base):
    __tablename__ = "timesheets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    hours = Column(Float, nullable=False)


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    team_id = Column(Integer, nullable=False)


class Holiday(Base):
    __tablename__ = "holidays"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    name = Column(String, nullable=False)