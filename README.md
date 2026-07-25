# AIVOA — AI-Powered Customer Complaint Management System

A full-stack, agentic complaint-intake system for the **pharmaceutical
manufacturing** industry (API & FDF Quality Management). An AI co-pilot reads a
free-text prompt, an email, or a PDF, **extracts** the complaint into a
structured QMS form, **reasons** about patient/quality risk, and stays editable
through natural-language corrections — the human never types into the form
directly.

Built for the AIVOA Round-1 Full-Stack assessment.

---

## Demo workflow (the three mandatory AI tools)

| Tool | How to trigger | What happens |
|------|----------------|--------------|
| **1. Log complaint** | Type a free-text complaint, e.g. *"Apollo Pharmacy reported discolored capsules in Amoxicillin capsules 500 mg"* | Agent extracts fields → fills the form → reasons the risk assessment |
| **2. Edit complaint** | Type a correction, e.g. *"Sorry, the batch number is BMX24602 and the affected quantity is 48 capsules"* | Agent updates **only** those fields, **preserves everything else**, re-assesses risk |
| **3. Document extraction** | Upload `backend/sample_data/metformin_api_complaint.pdf` | Agent extracts from the PDF → fills the form; still editable by chat afterwards |

Sample documents (2 PDFs + 1 email) are in [`backend/sample_data/`](backend/sample_data).

---

## Tech stack (as mandated)

- **Frontend:** React + **Redux Toolkit** (Vite), Google **Inter** font
- **Backend:** Python + **FastAPI**
- **AI agent framework:** **LangGraph**
- **LLMs:** **Groq** — `llama-3.3-70b-versatile` (extraction & risk reasoning) and
  `llama-3.1-8b-instant` (fast intent routing — the assignment names
  `gemma2-9b-it`, which Groq has since decommissioned; this is its current
  small/fast equivalent, and it's a one-line config change to swap back)
- **Database:** Postgres / MySQL (SQLAlchemy; SQLite fallback for zero-setup dev)

---

## Architecture

```
React + Redux  ──HTTP──>  FastAPI  ──>  LangGraph agent  ──>  Groq
   (two-panel UI)          (routes)      (state machine)     (LLMs)
                              │
                              └──>  Postgres  (complaints, ai_runs audit trail)
```

### The LangGraph agent

```
START ─> router ──(intent)──> log_complaint  ─┐
                          ──> extract_document ┼─> assess_risk ─> summarize_complaint ─> check_completeness ─> respond ─> END
                          ──> edit_complaint  ─┘
                          ──> answer_question ─────────────────────────────────────────────────────────────> END
```

- **`router`** classifies each turn into `log` / `edit` / `document` / `question`
  (uploads always take the `document` path; a keyword fast-path catches
  corrections cheaply before falling back to the small model).
- **`log_complaint` / `extract_document` / `edit_complaint`** are the three
  mandatory tools. Each returns a **field delta**, never the whole form.
- **`assess_risk`** runs after *every* mutation, so the AI Co-pilot Risk
  Assessment is re-reasoned on both a log and an edit.
- **`summarize_complaint`** writes a short narrative summary of the current complaint.
- **`check_completeness`** flags mandatory fields still missing and has the
  assistant ask for them directly in chat, instead of leaving them silently blank.

### Key design decision — why edits preserve fields

Tools return only the fields they're confident about. A custom **merge reducer**
on the `form` state channel folds that delta into the running form, skipping
null/blank values:

```python
# backend/app/graph/state.py
def merge_dict(old, new):
    merged = dict(old or {})
    for k, v in (new or {}).items():
        if v in (None, "") or v == []:
            continue
        merged[k] = v
    return merged
```

Preservation is therefore a **structural property of the data flow**, not a
prompt we hope the model obeys. `"the batch number is BMX24602"` can only ever
add/overwrite the batch field — the product name, customer, and description are
untouched.

Multi-turn memory comes from a LangGraph **checkpointer** keyed by `session_id`,
so an edit turn loads the form produced by an earlier log/upload turn.

### Audit trail

Every AI decision writes an `ai_runs` row (model, intent, latency, raw output).
In a regulated QMS every automated decision must be **traceable** — this is what
makes the pipeline auditable rather than a black box.

---

## Project structure

```
backend/
  app/
    main.py              FastAPI app + CORS + startup
    config.py            env settings (Groq keys, DB URL, CORS)
    db.py  models.py     SQLAlchemy engine + Complaint / AiRun models
    schemas.py           Pydantic contracts (ComplaintForm, RiskAssessment, ...)
    services.py          run the agent, detect duplicates, log the audit trail
    document_utils.py    PDF / email text extraction (no OCR — out of scope)
    graph/
      state.py           ComplaintState + the delta-merge reducer  ★
      prompts.py         field schema + all prompt templates
      llm.py             Groq factory + robust JSON call (retry)
      nodes.py           router + 4 tools + risk + summary + completeness + respond
      build.py           graph assembly + checkpointer
    routes/              chat.py · upload.py · complaints.py
  sample_data/           sample PDFs + email for demonstration
frontend/
  src/
    store.js  api.js
    features/
      agentThunks.js     sendMessage / uploadDocument thunks
      chat|complaint|risk|summary/ *Slice.js   (multiple slices react to one thunk)
    components/          ComplaintForm · RiskAssessment · ChatAssistant · ComplaintHistory
```

---

## Setup

### Prerequisites
- Python 3.11+ and Node 18+
- A free Groq API key from <https://console.groq.com>

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # then edit .env and set GROQ_API_KEY
python -m uvicorn app.main:app --reload --port 8000
```

The API is at <http://localhost:8000> (health check: `/health`, docs: `/docs`).

> **Database:** the default `.env` points at Postgres. For an instant local run,
> set `DATABASE_URL=sqlite:///./complaints.db` instead. Tables are created
> automatically on startup.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173  (proxies /api to :8000)
```

---

## API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/chat` | All the chat-driven tools — log / edit / question |
| `POST` | `/api/upload` | Document extraction (multipart: `session_id`, `file`) |
| `POST` | `/api/complaints` | Persist the reviewed complaint |
| `GET`  | `/api/complaints` | List saved complaints (powers the Complaint History tab) |
| `GET`  | `/health` | Status + configured models |

---

## Bonus features implemented

- **AI risk classification** — severity, risk level, rationale, risk factors
- **Complaint summary** — short AI-written narrative of the current complaint
- **Completeness checker** — flags missing mandatory fields and asks for them in chat
- **Duplicate detection** — flags a repeat complaint on the same product + batch
  (the classic batch-level-problem signal), shown as a banner in the UI
- **Root-cause & CAPA recommendation** — generated in the risk node
- **Audit trail** (`ai_runs`) — traceability for every AI decision
- **Field provenance** — AI-filled fields carry an "AI" badge and flash on update
- **Complaint History** — a second tab listing every saved complaint, with a
  click-through detail view (not on the assignment's bonus list, added because
  a QMS is only useful if past complaints can be reviewed)

---

## Notes & honest scope

- OCR / production document parsing is intentionally out of scope (per the
  assignment); only text-based PDFs and emails are parsed.
- The LangGraph checkpointer is in-memory (`MemorySaver`) — swap for a Postgres
  checkpointer to persist sessions across restarts.
- Sample pharmaceutical data is fictional, for demonstration only.
