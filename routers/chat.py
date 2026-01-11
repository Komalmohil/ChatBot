from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from services.intent import detect_intent
from services.response import generate_response, _fetch_user
from models.schemas import ChatRequest

router = APIRouter()


@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    intent = detect_intent(req.message)
    label = intent["label"]
    score = intent["score"]
    user = _fetch_user(db, int(req.user_id))
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    user_info = {"id": user.id, "name": user.name, "role": user.role, "team_id": user.team_id}

    payload = generate_response(
        db=db,
        intent_label=label,
        intent_score=score,
        user_info=user_info,
        user_text=req.message,
    )
    return {"intent": {"label": label, "confidence": round(score, 3)}, "payload": payload}