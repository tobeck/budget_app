# ──────────────────────────────────────────────────────────────────────────────
# tests/ingest/test_seb.py
# ──────────────────────────────────────────────────────────────────────────────
"""Test for Ingestor for SEB bank statement CSV exports."""

# ruff: noqa: I001
from pathlib import Path

import pandas as pd

from budget_app.ingest.seb import SEBIngestor

FIXTURE = Path(__file__).parent.parent / "fixtures" / "seb" / "test_seb.csv"


def test_sniff_matches_fixture() -> None:
    head = "\n".join(FIXTURE.read_text(encoding="utf‑8").splitlines()[:5])
    assert SEBIngestor().sniff(head) is True


def test_parse_returns_canonical_df() -> None:
    df = SEBIngestor().ingest(FIXTURE)

    # Columns in right order
    assert list(df.columns) == [
        "date",
        "payee",
        "amount",
        "currency",
        "account_id",
    ]

    # At least one row and no NaNs in mandatory cols
    assert not df.empty
    assert df[["date", "amount", "currency", "account_id"]].notna().all().all()

    # Amounts must be numeric
    assert pd.api.types.is_float_dtype(df["amount"])
