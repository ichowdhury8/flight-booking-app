"""Engine, session factory and the declarative base.

SQLite on local disk. On Render the filesystem is ephemeral, so this file is
recreated and reseeded on every cold start — see PLAN.md R1. That is a deliberate
trade, and it has the side benefit of keeping the 14-day flight window always fresh.
"""

from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DB_PATH = Path(__file__).resolve().parent.parent / "flights.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread=False: FastAPI serves requests from a threadpool, and each
# request gets its own Session, so the connection is never actually shared.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    """FastAPI dependency — one session per request, always closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
