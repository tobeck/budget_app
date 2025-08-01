# ──────────────────────────────────────────────────────────────────────────────
# src/budget_app/ingest/base.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import abc
from pathlib import Path

import pandas as pd


class BankIngestor(abc.ABC):
    """Abstract base‑class for bank‑statement ingestors."""

    # ---- Public API ---------------------------------------------------------

    @abc.abstractmethod
    def sniff(self, sample: str, /) -> bool:  # noqa: D401 (imperative)
        """Return *True* when *sample* looks like this bank's export format."""

    @abc.abstractmethod
    def parse(self, csv_path: Path, /) -> pd.DataFrame:  # noqa: D401
        """Parse *csv_path* into the canonical DataFrame.

        Canonical schema (dtypes are pandas defaults):
            date        → datetime64[ns]
            payee       → str
            amount      → float64  (negative = debit)
            currency    → str      (ISO‑4217, e.g. "SEK")
            account_id  → str      (clearing‑nr + account‑nr)
        """

    # ---- Convenience --------------------------------------------------------

    def ingest(self, csv_path: Path, /) -> pd.DataFrame:  # noqa: D401
        """Gatekeeper that wraps :py:meth:`parse` with basic sanitation."""
        df = self.parse(csv_path)
        required = {"date", "payee", "amount", "currency", "account_id"}
        missing = required.difference(df.columns)
        if missing:
            raise ValueError(f"Parsed DataFrame missing columns: {missing}")
        return df
