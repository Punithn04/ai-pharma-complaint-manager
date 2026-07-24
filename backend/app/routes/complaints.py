"""Persist and list reviewed complaints."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Complaint
from ..schemas import ComplaintOut, SaveComplaintRequest

router = APIRouter(prefix="/api", tags=["complaints"])


@router.post("/complaints", response_model=ComplaintOut)
def save_complaint(req: SaveComplaintRequest, db: Session = Depends(get_db)) -> ComplaintOut:
    form = req.form.model_dump()
    complaint = Complaint(
        session_id=req.session_id,
        risk_assessment=req.risk.model_dump(),
        **form,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return ComplaintOut.model_validate(complaint)


@router.get("/complaints", response_model=list[ComplaintOut])
def list_complaints(db: Session = Depends(get_db)) -> list[ComplaintOut]:
    rows = db.execute(select(Complaint).order_by(Complaint.id.desc())).scalars().all()
    return [ComplaintOut.model_validate(r) for r in rows]
