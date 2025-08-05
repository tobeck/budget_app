# ──────────────────────────────────────────────────────────────────────────────
# tests/db/test_insert.py
# ──────────────────────────────────────────────────────────────────────────────

# ruff: noqa: I001

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from budget_app.ingest.seb import SEBIngestor
from budget_app.models import Base, Transaction
from budget_app.services.ingest_db import add_transactions

FIXTURE = Path(__file__).parent.parent / "fixtures" / "seb" / "test_seb.csv"


@pytest.fixture(scope="module")
@pytest.fixture(scope="module")
def db_session() -> Iterator[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False, future=True)
    Base.metadata.create_all(engine)
    _Session: sessionmaker[Session] = sessionmaker(bind=engine, autoflush=False, future=True)
    with _Session() as sess:
        yield sess


def test_add_transactions(db_session: Session) -> None:
    df = SEBIngestor().ingest(FIXTURE)
    inserted = add_transactions(db_session, df)
    assert inserted == len(df)

    # inserting again should insert zero new rows (dedup works)
    inserted_again = add_transactions(db_session, df)
    assert inserted_again == 0

    total = db_session.query(Transaction).count()
    assert total == len(df)
