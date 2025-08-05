# ──────────────────────────────────────────────────────────────────────────────
# alembic/versions/0001_initial.py
# ──────────────────────────────────────────────────────────────────────────────
"""Initial tables: accounts & transactions."""
# ruff: noqa: I001
from __future__ import annotations

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:  # noqa: D401 (imperative)
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("institution", sa.String(20), nullable=False),
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "account_id",
            sa.Integer,
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("payee", sa.String(255), nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("tx_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("raw", sa.JSON, nullable=True),
    )


def downgrade() -> None:  # noqa: D401
    op.drop_table("transactions")
    op.drop_table("accounts")
