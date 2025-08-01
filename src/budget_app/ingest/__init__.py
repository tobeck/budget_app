# ──────────────────────────────────────────────────────────────────────────────
# src/budget_app/ingest/__init__.py
# ──────────────────────────────────────────────────────────────────────────────
"""Ingestion plug‑in registry and helpers."""

from collections.abc import Iterable
from importlib import metadata
from pathlib import Path

from .base import BankIngestor

# ---------------------------------------------------------------------------
# Dynamic entry‑point discovery (optional but future‑proof).
# Each concrete ingestor can expose itself under the group
# "budget_app.ingestors" so third‑party packages can add banks without
# touching core code.
# ---------------------------------------------------------------------------


def _discover_entrypoint_ingestors() -> Iterable[type[BankIngestor]]:
    for ep in metadata.entry_points(group="budget_app.ingestors"):
        cls = ep.load()
        yield cls


# ---------------------------------------------------------------------------
# Public helper that finds an ingestor able to parse the given file.
# ---------------------------------------------------------------------------


def get_matching_ingestor(path: Path) -> BankIngestor | None:
    sample = path.read_text(encoding="utf‑8", errors="ignore").splitlines()[:5]
    head = "\n".join(sample)

    # Built‑in ingestors (imported lazily to avoid import cycles)
    from .seb import SEBIngestor  # noqa: WPS433 (import inside function)

    candidates: list[type[BankIngestor]] = [SEBIngestor]
    candidates.extend(_discover_entrypoint_ingestors())

    for cls in candidates:
        ing = cls()
        if ing.sniff(head):
            return ing
    return None


__all__ = ["BankIngestor", "get_matching_ingestor"]
