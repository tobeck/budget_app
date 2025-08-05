# ──────────────────────────────────────────────────────────────────────────────
# src/budget_app/services/ingest_db.py
# ──────────────────────────────────────────────────────────────────────────────
"""Service: insert a canonical DataFrame into the DB with dedup."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Final

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Account, Transaction

REQUIRED_COLS: Final = {"date", "payee", "amount", "currency", "account_id"}


def _json_safe(value: Any) -> Any:
    """Convert non‑JSON‑serialisable values (Timestamp/Datetime) to ISO strings."""
    if isinstance(value, (pd.Timestamp | datetime)):
        return value.isoformat()
    return value


def add_transactions(session: Session, df: pd.DataFrame) -> int:  # noqa: D401 (imperative)
    """Insert rows from *df* into *session*, skipping duplicates.

    *Deduping logic*
    ----------------
    • We `flush()` once so hashes of rows previously added in the same Session
      are visible to our in‑memory hash set.
    • We query **all** existing hashes in one round‑trip, then do O(1) look‑ups
      per row instead of N extra SELECTs.

    Returns the number of *new* `Transaction` objects attached to the session.
    """
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame missing required columns: {missing}")

    session.flush()

    existing_hashes: set[str] = {h for (h,) in session.execute(select(Transaction.tx_hash))}

    new_rows: list[Transaction] = []

    for row in df.itertuples(index=False):
        tx_hash = Transaction.calc_hash(
            row.account_id,
            str(row.date.date()),
            row.payee,
            row.amount,
            row.currency,
        )
        if tx_hash in existing_hashes:
            continue  # duplicate
        existing_hashes.add(tx_hash)

        account = Account.get_or_create(
            session=session, account_id=row.account_id, currency=row.currency
        )

        clean_raw = {k: _json_safe(v) for k, v in row._asdict().items()}

        new_rows.append(
            Transaction(
                account=account,
                date=row.date.date(),
                payee=row.payee,
                amount=row.amount,
                currency=row.currency,
                tx_hash=tx_hash,
                raw=clean_raw,
            )
        )

    session.add_all(new_rows)
    return len(new_rows)
