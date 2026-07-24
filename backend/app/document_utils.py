"""Extract plain text from uploaded complaint documents.

Production-grade OCR is explicitly out of scope for this assignment, so we only
handle text-based PDFs and plain text / email files.
"""
import io

from pypdf import PdfReader


def extract_text(filename: str, data: bytes) -> str:
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        return _extract_pdf(data)
    # .txt, .eml, .md, or unknown -> best-effort decode
    return data.decode("utf-8", errors="ignore")


def _extract_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    parts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(parts).strip()
