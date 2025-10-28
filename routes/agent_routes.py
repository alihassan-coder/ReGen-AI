from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import uuid4
from agent.tools import get_user_latest_form

from config.database_config import get_db
from routes.auth_routes import get_current_user
from models.tables_models import User
from agent.main_agent import get_agent


router = APIRouter(prefix="/agent", tags=["agent"])


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    thread_id: str


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    agent = get_agent()
    thread_id = req.thread_id or str(uuid4())
    # Fetch latest form now (avoid passing DB session into LangGraph state)
    form = get_user_latest_form(db, current_user.id)
    state = {
        "user_id": current_user.id,
        "form": form,
        "message": req.message,
    }
    result = agent.invoke(state, {"configurable": {"thread_id": thread_id}})
    reply = result.get("reply", "I'm here to help, but I couldn't generate a response.")
    return ChatResponse(reply=reply, thread_id=thread_id)


