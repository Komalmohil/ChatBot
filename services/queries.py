from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from datetime import date, timedelta
from db import get_db
from models import Employee, Timesheet, Project, Holiday  # Define SQLAlchemy models

def get_employee(user_id: int, db: Session):
    return db.query(Employee).filter(Employee.id == user_id).first()

def get_own_timesheet(user_id: int, db: Session):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    entries = db.query(Timesheet).filter(
        and_(Timesheet.employee_id == user_id, 
             Timesheet.date >= week_start, 
             Timesheet.date <= week_end)
    ).all()
    
    total_hours = sum(e.hours for e in entries)
    return {"week_start": week_start, "week_end": week_end, "total_hours": total_hours, "entries": [e.__dict__ for e in entries]}

def get_team_timesheet(member_id: int, db: Session):
    # Same as own but for member_id
    return get_own_timesheet(member_id, db)  # Reuse

def get_team_members(manager_id: int, db: Session):
    return db.query(Employee).filter(Employee.manager_id == manager_id).all()

def get_projects(employee_id: int, db: Session):
    return db.query(Project).filter(Project.employee_id == employee_id).all()

def get_holidays(upcoming: bool, db: Session):
    if upcoming:
        today = date.today()
        return db.query(Holiday).filter(Holiday.date > today).limit(5).all()
    return db.query(Holiday).all()

def get_member_id(name_hint: str, manager_id: int, db: Session):
    member = db.query(Employee).filter(
        and_(Employee.manager_id == manager_id, 
             func.lower(Employee.name).contains(name_hint.lower()))
    ).first()
    return member.id if member else None

def get_team_projects(manager_id: int, db: Session):
    team_ids = [m.id for m in get_team_members(manager_id, db)]
    projects = db.query(Project).filter(Project.employee_id.in_(team_ids)).all()
    return {p.name: p.client for p in projects}
