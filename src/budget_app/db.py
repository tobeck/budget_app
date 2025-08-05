# ──────────────────────────────────────────────────────────────────────────────
# src/budget_app/db.py
# ──────────────────────────────────────────────────────────────────────────────
"""SQLAlchemy engine & session factory."""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings
from .models import Base  # noqa: F401 (needed for metadata create_all)

settings = get_settings()
_engine = create_engine(settings.DATABASE_URL, echo=False, future=True)
SessionLocal: sessionmaker[Session] = sessionmaker(bind=_engine, autoflush=False, future=True)


@contextmanager
def session_scope() -> Iterator[Session]:  # pragma: no cover
    """Provide a transactional scope around a series of operations."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:  # noqa: BLE001 (re‑raise for caller)
        session.rollback()
        raise
    finally:
        session.close()
