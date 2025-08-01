# ──────────────────────────────────────────────────────────────────────────────
# src/budget_app/ingest/seb.py
# ──────────────────────────────────────────────────────────────────────────────
"""Ingestor for SEB bank statement CSV exports."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Final

import pandas as pd

from .base import BankIngestor

# Header fields we *expect* in a SEB export.  The exact Swedish labels vary
# depending on language settings; include both ENG & SWE to be safe.
DATE_COLS: Final = ["Bokföringsdatum", "Datum", "Date"]
AMOUNT_COLS: Final = ["Belopp", "Amount"]
DESC_COLS: Final = ["Text", "Meddelande", "Specifikation", "Description"]
ACCOUNT_ID_RE: Final = re.compile(r"^(?P<clearing>\d{4})\s*(?P<number>\d{7,10})$")


class SEBIngestor(BankIngestor):
    """Parse SEB *CSV* exports into canonical transaction rows."""

    BANK_CODE: Final = "SEB"

    # ---------------------------------------------------------------------
    # Quick heuristics to identify the file
    # ---------------------------------------------------------------------
    def sniff(self, sample: str, /) -> bool:  # noqa: D401 (imperative mood)
        return any(col in sample for col in DATE_COLS) and "SEB" not in sample

    # ---------------------------------------------------------------------
    # Main parser
    # ---------------------------------------------------------------------
    def parse(self, csv_path: Path, /) -> pd.DataFrame:  # noqa: D401
        # Detect delimiter automatically; SEB often uses ';' but older exports use ','
        df = pd.read_csv(csv_path, sep=None, engine="python", dtype=str)

        # --- Column harmonisation --------------------------------------
        colmap: dict[str, str] = {}
        for c in df.columns:
            if c in DATE_COLS:
                colmap[c] = "date"
            elif c in AMOUNT_COLS:
                colmap[c] = "amount"
            elif c in DESC_COLS:
                colmap[c] = "payee"
        df.rename(columns=colmap, inplace=True)

        # --- Account id -------------------------------------------------
        # SEB exports sometimes include an "Account" column with clearing+number
        account_col = next((c for c in df.columns if c.lower().startswith("konto")), None)
        if account_col:
            df["account_id"] = (
                df[account_col].astype(str).str.strip().replace({r"\s+": ""}, regex=True)
            )
        else:
            # Fallback: single‑account file → infer from filename
            df["account_id"] = csv_path.stem

        # --- Currency ---------------------------------------------------
        if "currency" not in df.columns:
            df["currency"] = "SEK"

        # --- Amount cleanup --------------------------------------------
        df["amount"] = (
            df["amount"]
            .str.replace(" ", "", regex=False)  # remove thousands sep spaces
            .str.replace(",", ".", regex=False)  # 1 234,56 → 1234.56
            .astype(float)
        )

        # --- Dates ------------------------------------------------------
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")

        # --- Payee ------------------------------------------------------
        df["payee"] = df["payee"].fillna("").astype(str).str.strip()

        # Keep only canonical columns in order
        return df[["date", "payee", "amount", "currency", "account_id"]]
