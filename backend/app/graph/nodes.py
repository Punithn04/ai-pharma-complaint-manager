"""LangGraph nodes.

Flow:
    START -> router --(intent)--> log_complaint  ─┐
                               -> extract_document ┼-> assess_risk -> check_completeness -> respond -> END
                               -> edit_complaint  ─┘
                               -> answer_question ------------------------------------------------> END

Every mutation node returns a *delta* on the `form` channel. The merge reducer
in state.py folds it into the running form, so edits preserve untouched fields.
`assess_risk` always runs after a mutation, so the risk panel is re-reasoned on
every log AND every edit — exactly the behaviour shown in the demo video.
`check_completeness` then flags any mandatory field still missing so `respond`
can ask the user for it directly in the chat, instead of leaving the form
silently blank.
"""
from __future__ import annotations

import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from ..config import settings
from . import prompts
from .llm import get_llm, structured_call

FIELD_LABELS = {
    "complaint_source": "Complaint Source",
    "customer_name": "Customer Name",
    "product_name": "Product Name",
    "product_strength_grade": "Product Strength/Grade",
    "batch_lot_number": "Batch/Lot Number",
    "manufacturing_date": "Manufacturing Date",
    "expiry_date": "Expiry Date",
    "quantity_affected": "Quantity Affected",
    "complaint_type": "Complaint Type",
    "complaint_date": "Complaint Date",
    "detailed_description": "Detailed Description",
    "initial_severity": "Initial Severity",
    "priority": "Priority",
}
ALLOWED_FIELDS = set(FIELD_LABELS)

# Fields a QMS record cannot go to investigation without. Initial_severity and
# priority are excluded — those are reasoned by assess_risk, not user-supplied.
MANDATORY_FIELDS = [
    "complaint_source",
    "product_name",
    "batch_lot_number",
    "manufacturing_date",
    "expiry_date",
    "quantity_affected",
    "complaint_type",
    "detailed_description",
]


def _last_user_text(state: dict) -> str:
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""


def _clean_form_delta(raw: dict) -> dict:
    """Keep only known fields with non-empty values."""
    form = raw.get("form", raw) if isinstance(raw, dict) else {}
    delta = {}
    for key, value in (form or {}).items():
        if key not in ALLOWED_FIELDS:
            continue
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        delta[key] = value.strip() if isinstance(value, str) else value
    return delta


# --------------------------------------------------------------------------- #
# Router
# --------------------------------------------------------------------------- #
def route_by_intent(state: dict) -> str:
    return state.get("intent", "question")


def router_node(state: dict) -> dict:
    # An uploaded document always takes the extraction path.
    if state.get("source") == "document":
        return {"intent": "document"}

    text = _last_user_text(state)
    has_form = bool(state.get("form"))

    # Heuristic fast-path: cheap and robust for the small routing model.
    # Kept narrow and correction-specific — a broad catch-all like a bare
    # "not " would misroute ordinary descriptive sentences ("did not receive
    # a replacement") into edits.
    lowered = text.lower()
    if has_form and any(
        kw in lowered
        for kw in ("sorry", "actually", "correction", "should be",
                   "instead of", "instead,", "the batch is", "the batch number",
                   "change it to", "change the", "update the", "correct the")
    ):
        return {"intent": "edit"}

    parsed, _ = structured_call(settings.groq_fast_model, prompts.ROUTER_SYSTEM, text)
    intent = str(parsed.get("intent", "")).lower()
    if intent not in {"log", "edit", "question"}:
        intent = "edit" if has_form else "log"
    # Can't edit what doesn't exist yet.
    if intent == "edit" and not has_form:
        intent = "log"
    return {"intent": intent}


# --------------------------------------------------------------------------- #
# Extraction tools (log / document / edit)
# --------------------------------------------------------------------------- #
def log_node(state: dict) -> dict:
    text = _last_user_text(state)
    parsed, _ = structured_call(settings.groq_extraction_model, prompts.EXTRACT_SYSTEM, text)
    delta = _clean_form_delta(parsed)
    return {"form": delta, "changed_fields": list(delta), "model_used": settings.groq_extraction_model}


def document_node(state: dict) -> dict:
    text = state.get("document_text") or _last_user_text(state)
    user = f"Extract the complaint from this document:\n\n{text}"
    parsed, _ = structured_call(settings.groq_extraction_model, prompts.EXTRACT_SYSTEM, user)
    delta = _clean_form_delta(parsed)
    return {"form": delta, "changed_fields": list(delta), "model_used": settings.groq_extraction_model}


def edit_node(state: dict) -> dict:
    text = _last_user_text(state)
    current = json.dumps(state.get("form", {}), indent=2)
    user = f"Current form:\n{current}\n\nUser correction:\n{text}"
    parsed, _ = structured_call(settings.groq_extraction_model, prompts.EDIT_SYSTEM, user)
    delta = _clean_form_delta(parsed)
    return {"form": delta, "changed_fields": list(delta), "model_used": settings.groq_extraction_model}


# --------------------------------------------------------------------------- #
# Risk assessment (AI co-pilot)
# --------------------------------------------------------------------------- #
def assess_risk_node(state: dict) -> dict:
    form = state.get("form", {})
    if not form:
        return {}
    user = f"Current complaint:\n{json.dumps(form, indent=2)}"
    parsed, _ = structured_call(settings.groq_extraction_model, prompts.RISK_SYSTEM, user)
    if not isinstance(parsed, dict):
        return {}
    # Normalise: ensure risk_factors is a list.
    if isinstance(parsed.get("risk_factors"), str):
        parsed["risk_factors"] = [parsed["risk_factors"]]
    return {"risk": parsed}


# --------------------------------------------------------------------------- #
# Complaint summary (bonus tool)
# --------------------------------------------------------------------------- #
def summarize_node(state: dict) -> dict:
    form = state.get("form") or {}
    if not form:
        return {}
    user = f"Current complaint:\n{json.dumps(form, indent=2)}"
    parsed, _ = structured_call(settings.groq_extraction_model, prompts.SUMMARIZE_SYSTEM, user)
    summary = parsed.get("summary") if isinstance(parsed, dict) else None
    if not summary or not str(summary).strip():
        return {}
    return {"summary": str(summary).strip()}


# --------------------------------------------------------------------------- #
# Q&A
# --------------------------------------------------------------------------- #
def answer_node(state: dict) -> dict:
    text = _last_user_text(state)
    form = json.dumps(state.get("form", {}), indent=2)
    llm = get_llm(settings.groq_fast_model)

    resp = llm.invoke([
        SystemMessage(content=prompts.ANSWER_SYSTEM),
        HumanMessage(content=f"Current complaint form:\n{form}\n\nQuestion: {text}"),
    ])
    reply = resp.content if isinstance(resp.content, str) else str(resp.content)
    return {"reply": reply, "messages": [AIMessage(content=reply)]}


# --------------------------------------------------------------------------- #
# Completeness checker (bonus tool)
# --------------------------------------------------------------------------- #
def check_completeness_node(state: dict) -> dict:
    """Flag mandatory fields still missing after extraction/edit, so `respond`
    can ask the user for them directly instead of leaving the form silently
    incomplete."""
    form = state.get("form") or {}
    if not form:
        return {"missing_fields": []}
    missing = [f for f in MANDATORY_FIELDS if not str(form.get(f) or "").strip()]
    return {"missing_fields": missing}


# --------------------------------------------------------------------------- #
# Compose the assistant's chat reply for mutation intents
# --------------------------------------------------------------------------- #
def respond_node(state: dict) -> dict:
    intent = state.get("intent", "log")
    changed = state.get("changed_fields", []) or []
    risk = state.get("risk", {}) or {}
    missing = state.get("missing_fields", []) or []
    labels = [FIELD_LABELS.get(f, f) for f in changed]

    if not changed:
        reply = ("I couldn't confidently extract any complaint fields from that. "
                 "Could you add a bit more detail (product, batch, what went wrong)?")
        return {"reply": reply, "messages": [AIMessage(content=reply)]}

    if intent == "edit":
        head = f"Updated {', '.join(labels)}."
    elif intent == "document":
        head = f"Extracted {len(changed)} field(s) from the document: {', '.join(labels)}."
    else:
        head = f"Logged the complaint and filled {len(changed)} field(s): {', '.join(labels)}."

    risk_bits = []
    if risk.get("severity"):
        risk_bits.append(f"severity **{risk['severity']}**")
    if risk.get("next_action"):
        risk_bits.append(f"recommended action: {risk['next_action']}")
    tail = f" Risk assessment — {'; '.join(risk_bits)}." if risk_bits else ""

    missing_tail = ""
    if missing:
        missing_labels = [FIELD_LABELS.get(f, f) for f in missing]
        missing_tail = (
            f"\n\n⚠️ A few required fields are still empty — please tell me: "
            f"{', '.join(missing_labels)}."
        )

    reply = head + tail + missing_tail
    return {"reply": reply, "messages": [AIMessage(content=reply)]}
