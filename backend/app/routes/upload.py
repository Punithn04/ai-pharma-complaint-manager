"""Document extraction endpoint (mandatory tool #3).

Extracts text from the uploaded PDF/email, then feeds it through the SAME graph
with source="document". Because state is keyed by session_id, the extracted
complaint remains editable by natural-language chat afterwards.
"""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..db import get_db
from ..document_utils import extract_text
from ..schemas import ChatResponse
from ..services import run_agent

router = APIRouter(prefix="/api", tags=["upload"])

MAX_BYTES = 10 * 1024 * 1024  # 10 MB, matches the reference UI


@router.post("/upload", response_model=ChatResponse)
async def upload(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ChatResponse:
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 10 MB limit.")

    text = extract_text(file.filename, data)
    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="Could not extract any text from the document (scanned images "
                   "are not supported — OCR is out of scope).",
        )

    result = run_agent(
        db,
        session_id=session_id,
        message=f"[Document uploaded: {file.filename}]",
        source="document",
        document_text=text,
    )
    return ChatResponse(**result)
