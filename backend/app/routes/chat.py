"""Chat endpoint — the single entry point for all three mandatory AI tools.

The agent decides (via the router node) whether the message is a new complaint
(log), a correction (edit), or a question. One endpoint, three tools.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import ChatRequest, ChatResponse
from ..services import run_agent

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    result = run_agent(db, session_id=req.session_id, message=req.message, source="chat")
    return ChatResponse(**result)
