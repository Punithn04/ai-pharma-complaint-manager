"""ORM models.

Complaint  - the reviewed, saved complaint record.
AiRun      - audit trail. Every AI decision in a regulated (pharma QMS)
             system must be traceable: which model ran, what it returned,
             how long it took. This table is what makes the pipeline auditable.
"""
import datetime as dt

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)

    # Origin & customer
    complaint_source: Mapped[str | None] = mapped_column(String(255))
    customer_name: Mapped[str | None] = mapped_column(String(255))

    # Product & batch
    product_name: Mapped[str | None] = mapped_column(String(255), index=True)
    product_strength_grade: Mapped[str | None] = mapped_column(String(120))
    batch_lot_number: Mapped[str | None] = mapped_column(String(120), index=True)
    manufacturing_date: Mapped[str | None] = mapped_column(String(40))
    expiry_date: Mapped[str | None] = mapped_column(String(40))
    quantity_affected: Mapped[str | None] = mapped_column(String(120))

    # Complaint details
    complaint_type: Mapped[str | None] = mapped_column(String(120))
    complaint_date: Mapped[str | None] = mapped_column(String(40))
    detailed_description: Mapped[str | None] = mapped_column(Text)

    # Initial assessment
    initial_severity: Mapped[str | None] = mapped_column(String(40))
    priority: Mapped[str | None] = mapped_column(String(40))

    # AI co-pilot risk assessment (reasoned, stored as JSON snapshot)
    risk_assessment: Mapped[dict | None] = mapped_column(JSON)
    # AI-generated narrative summary (bonus tool: summarize_complaint)
    summary: Mapped[str | None] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(40), default="Pending Triage")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow)


class AiRun(Base):
    __tablename__ = "ai_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    intent: Mapped[str | None] = mapped_column(String(40))
    model: Mapped[str | None] = mapped_column(String(120))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[float | None] = mapped_column(Float)
    output_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow)
