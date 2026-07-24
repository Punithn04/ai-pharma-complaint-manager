"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import init_db
from .routes import chat, complaints, upload

app = FastAPI(title="AIVOA Complaint Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(complaints.router)


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "extraction_model": settings.groq_extraction_model,
        "fast_model": settings.groq_fast_model,
        "groq_configured": bool(settings.groq_api_key),
    }
