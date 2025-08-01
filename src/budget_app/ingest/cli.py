# ──────────────────────────────────────────────────────────────────────────────
# src/budget_app/ingest/cli.py
# ──────────────────────────────────────────────────────────────────────────────
"""Tiny CLI for ad‑hoc ingestion tests.

Usage::

    poetry run budget ingest path/to/file.csv  >  normalized.csv
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import typer

from . import get_matching_ingestor

app = typer.Typer(help="Ingest bank‑statement files and output canonical CSV.")


@app.command()
def ingest(path: Path) -> None:  # noqa: D401 (imperative)
    """Parse *path* and stream canonical CSV to stdout."""
    ingestor = get_matching_ingestor(path)
    if ingestor is None:
        typer.echo("❌ No ingestor found for this file.", err=True)
        raise typer.Exit(code=1)

    df = ingestor.ingest(path)

    # Stream to stdout so you can pipe/redirect
    df.to_csv(sys.stdout, index=False, quoting=csv.QUOTE_MINIMAL)


if __name__ == "__main__":  # pragma: no cover
    app()
