"""End-to-end HTTP test of the API with the LLM mocked.

Exercises routes -> services -> graph -> DB (SQLite) offline, so no Groq key is
needed. Verifies: log fills the form + risk, edit preserves other fields over
HTTP, save persists, and a repeat product+batch is flagged as a duplicate.
"""
import os

os.environ["DATABASE_URL"] = "sqlite:///./test_api.db"
os.environ["GROQ_API_KEY"] = "test-key"

import sys  # noqa: E402
from unittest.mock import patch  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

from app.graph import prompts  # noqa: E402
from app.main import app  # noqa: E402


def _fake_structured_call(model, system, user, temperature=0.0):
    if system == prompts.ROUTER_SYSTEM:
        return {"intent": "log"}, 5
    if system == prompts.EXTRACT_SYSTEM:
        return ({"form": {
            "complaint_source": "Apollo Pharmacy",
            "product_name": "Amoxicillin Capsules",
            "product_strength_grade": "500 mg",
            "complaint_type": "Quality Defect",
            "detailed_description": "Discolored capsules.",
        }}, 10)
    if system == prompts.EDIT_SYSTEM:
        return ({"form": {"batch_lot_number": "BMX24602",
                          "quantity_affected": "48 capsules"}}, 8)
    if system == prompts.RISK_SYSTEM:
        return ({"severity": "Major", "risk_level": "Medium",
                 "next_action": "Route to QA investigation and issue replacement",
                 "risk_factors": ["Visual defect"]}, 12)
    return {}, 1


def test_full_http_flow():
    # `with TestClient(app)` fires the startup event, which creates the tables.
    with patch("app.graph.nodes.structured_call", _fake_structured_call), \
            TestClient(app) as client:

        assert client.get("/health").json()["status"] == "ok"

        sid = "http-test-1"

        # 1) Log
        r1 = client.post("/api/chat", json={
            "session_id": sid,
            "message": "Apollo Pharmacy reported discolored Amoxicillin 500mg capsules",
        }).json()
        assert r1["intent"] == "log"
        assert r1["form"]["product_name"] == "Amoxicillin Capsules"
        assert r1["risk"]["severity"] == "Major"

        # 2) Edit — preserve everything except batch + quantity
        r2 = client.post("/api/chat", json={
            "session_id": sid,
            "message": "Sorry, the batch number is BMX24602 and quantity is 48 capsules",
        }).json()
        assert r2["intent"] == "edit"
        assert r2["form"]["batch_lot_number"] == "BMX24602"
        assert r2["form"]["product_name"] == "Amoxicillin Capsules"   # preserved
        assert r2["form"]["complaint_source"] == "Apollo Pharmacy"    # preserved

        # 3) Save
        saved = client.post("/api/complaints", json={
            "session_id": sid,
            "form": r2["form"],
            "risk": r2["risk"],
        }).json()
        assert isinstance(saved["id"], int)

        # 4) Duplicate detection — a new session with same product+batch
        r3 = client.post("/api/chat", json={
            "session_id": "http-test-2",
            "message": "Apollo Pharmacy reported discolored Amoxicillin 500mg capsules",
        }).json()
        client.post("/api/chat", json={
            "session_id": "http-test-2",
            "message": "Sorry, the batch number is BMX24602",
        })
        # re-run through chat to trigger duplicate lookup on merged form
        r4 = client.post("/api/chat", json={
            "session_id": "http-test-2",
            "message": "What severity did you assign?",
        }).json()
        # product+batch now match the saved complaint
        assert r4["duplicate_of"] == saved["id"]

    print("PASS: log + edit(preserve) + save + duplicate detection over HTTP.")


if __name__ == "__main__":
    test_full_http_flow()
    # cleanup
    try:
        os.remove("./test_api.db")
    except OSError:
        pass
