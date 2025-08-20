# ──────────────────────────────────────────────────────────────────────────────
# src/budget_app/services/ingest_db.py
# ──────────────────────────────────────────────────────────────────────────────
"""Service: insert a canonical DataFrame into the DB with dedup."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Final, cast

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Account, Transaction

REQUIRED_COLS: Final = {"date", "payee", "amount", "currency", "account_id"}


def _json_safe(value: Any) -> Any:
    """Convert non-JSON-serialisable values to JSON-friendly primitives."""
    if isinstance(value, (pd.Timestamp, datetime, date)):  # noqa: UP038
        # date has .isoformat too and is JSON-friendly as a string
        return value.isoformat()
    return value


def _coerce_date(value: Any) -> date:
    """Coerce mixed date-like values into a `datetime.date`."""
    if isinstance(value, pd.Timestamp):
        return cast(date, value.date())
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    # Fallback for numpy.datetime64 / other scalars:
    ts = cast(pd.Timestamp, pd.to_datetime(value))
    return cast(date, ts.date())


def add_transactions(session: Session, df: pd.DataFrame) -> int:  # noqa: D401
    """Insert *df* into *session*, skipping rows whose hash already exists."""
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame missing required columns: {missing}")

    session.flush()  # make unflushed inserts visible to our SELECT

    existing_hashes: set[str] = {h for (h,) in session.execute(select(Transaction.tx_hash))}
    new_rows: list[Transaction] = []

    # Iterate with well-typed dicts instead of itertuples() to avoid giant unions
    for rec in df.to_dict(orient="records"):
        account_id = str(rec["account_id"])
        date_obj = _coerce_date(rec["date"])
        date_iso = date_obj.isoformat()
        payee = str(rec["payee"])
        amount = float(rec["amount"])
        currency = str(rec["currency"])

        tx_hash = Transaction.calc_hash(account_id, date_iso, payee, amount, currency)
        if tx_hash in existing_hashes:
            continue
        existing_hashes.add(tx_hash)

        account = Account.get_or_create(
            session=session,
            account_id=account_id,
            currency=currency,
        )

        clean_raw = {k: _json_safe(v) for k, v in rec.items()}

        new_rows.append(
            Transaction(
                account=account,
                date=date_obj,
                payee=payee,
                amount=amount,
                currency=currency,
                tx_hash=tx_hash,
                raw=clean_raw,
            )
        )

    session.add_all(new_rows)
    return len(new_rows)
