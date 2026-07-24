"""SQLAlchemy engine, session factory and Base.

DATABASE_URL is DB-agnostic: point it at Postgres/MySQL for the mandatory
stack, or leave the SQLite default for a zero-setup local run.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

# check_same_thread is only needed for SQLite; harmless to compute conditionally.
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create tables. Imported models must be registered before calling."""
    from . import models  # noqa: F401  (ensures models are registered on Base)

    Base.metadata.create_all(bind=engine)
