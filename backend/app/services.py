"""Agent service: run the LangGraph agent, detect duplicates, write the audit trail.

Keeps DB concerns (duplicate lookup, AiRun logging) out of the graph itself so
the graph stays a pure state machine that is trivial to unit-test.
"""
from __future__ import annotations

import time

from langchain_core.messages import HumanMessage
from sqlalchemy import select
from sqlalchemy.orm import Session

from .graph.build import graph
from .models import AiRun, Complaint


def _detect_duplicate(db: Session, form: dict) -> int | None:
    """A repeat complaint on the same product + batch is the classic pharma
    signal for a batch-level problem. Flag it (don't block)."""
    product = (form.get("product_name") or "").strip()
    batch = (form.get("batch_lot_number") or "").strip()
    if not product or not batch:
        return None
    stmt = (
        select(Complaint.id)
        .where(Complaint.product_name.ilike(product))
        .where(Complaint.batch_lot_number.ilike(batch))
        .order_by(Complaint.id.desc())
    )
    return db.execute(stmt).scalars().first()


def run_agent(
    db: Session,
    session_id: str,
    message: str,
    source: str = "chat",
    document_text: str | None = None,
) -> dict:
    started = time.perf_counter()

    state_input: dict = {"source": source}
    if document_text is not None:
        state_input["document_text"] = document_text
    if message:
        state_input["messages"] = [HumanMessage(content=message)]

    config = {"configurable": {"thread_id": session_id}}
    result = graph.invoke(state_input, config=config)

    form = result.get("form", {}) or {}
    risk = result.get("risk", {}) or {}
    intent = result.get("intent", "log")
    reply = result.get("reply", "")
    changed = result.get("changed_fields", []) or []
    missing = result.get("missing_fields", []) or []
    summary = result.get("summary") or None
    model_used = result.get("model_used")
    latency_ms = int((time.perf_counter() - started) * 1000)

    duplicate_of = _detect_duplicate(db, form)

    # --- audit trail ---------------------------------------------------------
    db.add(AiRun(
        session_id=session_id,
        intent=intent,
        model=model_used,
        latency_ms=latency_ms,
        output_json={
            "form": form, "risk": risk,
            "changed_fields": changed, "missing_fields": missing, "summary": summary,
        },
    ))
    db.commit()

    return {
        "session_id": session_id,
        "intent": intent,
        "reply": reply,
        "form": form,
        "risk": risk,
        "changed_fields": changed,
        "missing_fields": missing,
        "summary": summary,
        "duplicate_of": duplicate_of,
    }
