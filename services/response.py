from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from models.schemas import User, Timesheet, Project, Holiday
from datetime import date


# Role helpers
ALLOWED_TEAM_TIMESHEET_ROLES = {"teamlead", "manager", "hr", "admin"}
ALLOWED_TEAM_MEMBERS_ROLES = {"teamlead", "manager"}
ALL_ROLES = {"employee", "teamlead", "manager", "hr", "admin"}


def _suggest(message: str) -> str:
    return f"{message} If you want, try asking more specifically—like a name, a date range, or 'list my team'."


def _personalize(name: str, text: str) -> str:
    return f"{name}, {text}" if name else text


def _fetch_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def _fetch_timesheet(db: Session, user_id: int) -> List[Timesheet]:
    return db.query(Timesheet).filter(Timesheet.user_id == user_id).order_by(Timesheet.date.desc()).all()


def _fetch_team_members(db: Session, team_id: Optional[int]) -> List[User]:
    if team_id is None:
        return []
    return db.query(User).filter(User.team_id == team_id).all()


def _fetch_projects_for_team(db: Session, team_id: Optional[int]) -> List[Project]:
    if team_id is None:
        return []
    return db.query(Project).filter(Project.team_id == team_id).all()


def _fetch_projects_for_user(db: Session, user_id: int, team_id: Optional[int]) -> List[Project]:
    # Simple assumption: user works on projects of their team
    if team_id is None:
        return []
    return db.query(Project).filter(Project.team_id == team_id).all()


def _fetch_holidays(db: Session) -> List[Holiday]:
    return db.query(Holiday).order_by(Holiday.date.asc()).all()


def generate_response(
    db: Session,
    intent_label: str,
    intent_score: float,
    user_info: Dict[str, Any],
    user_text: str,
) -> Dict[str, Any]:
    """
    Returns a structured response payload with:
    - type: 'message' | 'timesheet' | 'list' | 'selection' | 'holidays'
    - data: payload
    - follow_up: optional suggestive prompt
    """
    role = (user_info.get("role") or "").lower()
    user_id = int(user_info.get("id"))
    user_name = user_info.get("name") or ""
    team_id = user_info.get("team_id")

    # Confidence gate—if low, be suggestive
    if intent_score < 0.25:
        return {
            "type": "message",
            "data": _personalize(user_name, "I’m not fully sure what you meant."),
            "follow_up": _suggest("Do you want your timesheet, your projects, or upcoming holidays?"),
        }

    # Intent routing
    if intent_label == "view_own_timesheet":
        entries = _fetch_timesheet(db, user_id)
        if not entries:
            return {
                "type": "message",
                "data": _personalize(user_name, "I couldn’t find any timesheet entries for you."),
                "follow_up": _suggest("You can add a date range like 'my timesheet for last week'."),
            }
        return {
            "type": "timesheet",
            "data": {
                "user_id": user_id,
                "user_name": user_name,
                "entries": [{"date": e.date.isoformat(), "hours": e.hours} for e in entries],
            },
        }

    if intent_label == "view_teammate_timesheet":
        if role in ALLOWED_TEAM_TIMESHEET_ROLES:
            # Suggest selection flow rather than exposing directly
            members = _fetch_team_members(db, team_id)
            if not members:
                return {
                    "type": "message",
                    "data": _personalize(user_name, "I don’t see any members in your team."),
                }
            return {
                "type": "selection",
                "data": {
                    "prompt": "Do you want all team timesheets or select a member?",
                    "options": [{"id": m.id, "name": m.name} for m in members],
                },
                "follow_up": "Reply with 'all team timesheets' or a member name/id.",
            }
        return {
            "type": "message",
            "data": _personalize(user_name, "You’re not authorized to view a teammate’s timesheet."),
            "follow_up": "You can still view your own timesheet—try 'my timesheet'.",
        }

    if intent_label == "view_team_timesheet":
        if role in ALLOWED_TEAM_TIMESHEET_ROLES:
            members = _fetch_team_members(db, team_id)
            if not members:
                return {
                    "type": "message",
                    "data": _personalize(user_name, "Your team looks empty right now."),
                }
            return {
                "type": "selection",
                "data": {
                    "prompt": "Do you want to see all members or pick one?",
                    "options": [{"id": m.id, "name": m.name} for m in members],
                },
                "follow_up": "Say 'all' or provide a member name/id.",
            }
        return {
            "type": "message",
            "data": _personalize(user_name, "You’re not authorized to view team timesheets."),
            "follow_up": "You can ask for your own timesheet.",
        }

    if intent_label == "view_team_members":
        if role in ALLOWED_TEAM_MEMBERS_ROLES:
            members = _fetch_team_members(db, team_id)
            projects = _fetch_projects_for_team(db, team_id)
            proj_by_team = {p.id: p.name for p in projects}
            # Simple mapping: show members and team projects (no per-user assignment in seed)
            return {
                "type": "list",
                "data": {
                    "members": [{"id": m.id, "name": m.name} for m in members],
                    "projects": [{"id": p.id, "name": p.name} for p in projects],
                },
                "follow_up": "Ask 'timesheet of <member name>' or 'team timesheets'.",
            }
        return {
            "type": "message",
            "data": _personalize(user_name, "You’re not authorized to view who’s under you."),
            "follow_up": "You can still ask for your projects or holidays.",
        }

    if intent_label == "view_own_details":
        u = _fetch_user(db, user_id)
        if not u:
            return {"type": "message", "data": _personalize(user_name, "I couldn’t find your profile.")}
        return {
            "type": "list",
            "data": {
                "id": u.id,
                "name": u.name,
                "role": u.role,
                "team_id": u.team_id,
            },
        }

    if intent_label == "view_own_projects":
        projects = _fetch_projects_for_user(db, user_id, team_id)
        if not projects:
            return {
                "type": "message",
                "data": _personalize(user_name, "I don’t see any active projects for you."),
                "follow_up": "If you recently switched teams, say 'my team projects'.",
            }
        return {
            "type": "list",
            "data": [{"id": p.id, "name": p.name} for p in projects],
        }

    if intent_label == "view_holidays":
        holidays = _fetch_holidays(db)
        return {
            "type": "holidays",
            "data": [{"date": h.date.isoformat(), "name": h.name} for h in holidays],
        }

    # Out of scope—personalized, suggestive
    return {
        "type": "message",
        "data": _personalize(user_name, "That’s outside what I can handle right now."),
        "follow_up": "Try asking for your timesheet, your projects, your details, or upcoming holidays.",
    }