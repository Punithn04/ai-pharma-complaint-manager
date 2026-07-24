"""The crux test: an edit must update only the mentioned fields and PRESERVE
everything else.

The LLM is mocked, so this runs offline (no Groq key needed) and tests the
graph's data flow — the delta-merge reducer — not the model. Run with:

    pytest tests/test_preservation.py            # or
    python tests/test_preservation.py
"""
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage  # noqa: E402

from app.graph import prompts  # noqa: E402


def _fake_structured_call(model, system, user, temperature=0.0):
    """Return canned JSON depending on which prompt was used."""
    if system == prompts.ROUTER_SYSTEM:
        return {"intent": "log"}, 5
    if system == prompts.EXTRACT_SYSTEM:
        return ({
            "form": {
                "complaint_source": "Apollo Pharmacy",
                "customer_name": "Apollo Pharmacy",
                "product_name": "Amoxicillin Capsules",
                "product_strength_grade": "500 mg",
                "complaint_type": "Quality Defect",
                "detailed_description": "Discolored capsules reported.",
            }
        }, 10)
    if system == prompts.EDIT_SYSTEM:
        # The user only mentioned batch + quantity -> delta contains ONLY those.
        return ({
            "form": {
                "batch_lot_number": "BMX24602",
                "quantity_affected": "48 capsules",
            }
        }, 8)
    if system == prompts.RISK_SYSTEM:
        return ({
            "severity": "Major",
            "risk_level": "Medium",
            "next_action": "Route to QA investigation and issue replacement",
            "risk_factors": ["Visual defect", "Distributed batch"],
        }, 12)
    return {}, 1


def test_edit_preserves_fields():
    with patch("app.graph.nodes.structured_call", _fake_structured_call):
        from app.graph.build import build_graph

        graph = build_graph()
        cfg = {"configurable": {"thread_id": "test-session"}}

        # 1) Log a fresh complaint.
        s1 = graph.invoke(
            {"source": "chat",
             "messages": [HumanMessage(content="Apollo Pharmacy reported discolored "
                                               "Amoxicillin capsules 500 mg")]},
            config=cfg,
        )
        form1 = s1["form"]
        assert form1["product_name"] == "Amoxicillin Capsules"
        assert form1["product_strength_grade"] == "500 mg"
        assert form1.get("batch_lot_number") in (None, "")  # not known yet
        assert s1["risk"]["severity"] == "Major"

        # 2) Edit: correct ONLY the batch number and quantity.
        s2 = graph.invoke(
            {"source": "chat",
             "messages": [HumanMessage(content="Sorry, the batch number is BMX24602 "
                                               "and the affected quantity is 48 capsules")]},
            config=cfg,
        )
        form2 = s2["form"]

        # The mentioned fields updated...
        assert form2["batch_lot_number"] == "BMX24602"
        assert form2["quantity_affected"] == "48 capsules"

        # ...and EVERYTHING ELSE is preserved.
        assert form2["product_name"] == "Amoxicillin Capsules"
        assert form2["product_strength_grade"] == "500 mg"
        assert form2["customer_name"] == "Apollo Pharmacy"
        assert form2["complaint_type"] == "Quality Defect"
        assert form2["detailed_description"] == "Discolored capsules reported."

        # Risk was re-assessed on the edit too.
        assert form2["batch_lot_number"] == "BMX24602"
        assert s2["risk"]["next_action"]

    print("PASS: edit updated batch + quantity and preserved all other fields.")


if __name__ == "__main__":
    test_edit_preserves_fields()
