"""Pydantic schemas shared between the API and the LangGraph agent.

All ComplaintForm fields are Optional: the AI fills what it can extract and
leaves the rest for later turns. This is what makes partial extraction and
field-preserving edits possible.
"""
import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field


class ComplaintForm(BaseModel):
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength_grade: Optional[str] = None
    batch_lot_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    quantity_affected: Optional[str] = None
    complaint_type: Optional[str] = None
    complaint_date: Optional[str] = None
    detailed_description: Optional[str] = None
    initial_severity: Optional[str] = None
    priority: Optional[str] = None


class RiskAssessment(BaseModel):
    severity: Optional[str] = None            # Critical | Major | Minor
    risk_level: Optional[str] = None          # High | Medium | Low
    next_action: Optional[str] = None
    rationale: Optional[str] = None
    risk_factors: list[str] = Field(default_factory=list)
    potential_root_cause: Optional[str] = None
    capa_recommendation: Optional[str] = None


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    intent: str
    reply: str
    form: dict
    risk: dict
    changed_fields: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    summary: Optional[str] = None
    duplicate_of: Optional[int] = None


class SaveComplaintRequest(BaseModel):
    session_id: str
    form: ComplaintForm
    risk: RiskAssessment
    summary: Optional[str] = None


class ComplaintOut(BaseModel):
    """Powers the Complaint History tab — the table row AND the full detail
    view when a row is clicked, so it carries every ComplaintForm field."""
    id: int
    created_at: dt.datetime
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength_grade: Optional[str] = None
    batch_lot_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    quantity_affected: Optional[str] = None
    complaint_type: Optional[str] = None
    complaint_date: Optional[str] = None
    detailed_description: Optional[str] = None
    initial_severity: Optional[str] = None
    priority: Optional[str] = None
    status: str
    risk_assessment: Optional[dict] = None
    summary: Optional[str] = None

    class Config:
        from_attributes = True
