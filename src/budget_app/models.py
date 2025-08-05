# ──────────────────────────────────────────────────────────────────────────────
# src/budget_app/models.py
# ──────────────────────────────────────────────────────────────────────────────
"""ORM models for accounts & transactions (type‑checked)."""
from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any, Self

from sqlalchemy import JSON, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarative class for SQLAlchemy 2 ORM."""


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="SEK")
    institution: Mapped[str] = mapped_column(String(20), nullable=False, default="SEB")

    transactions: Mapped[list[Transaction]] = relationship(
        back_populates="account",
        cascade="all,delete-orphan",
    )

    # Convenience factory --------------------------------------------------
    @classmethod
    def get_or_create(
        cls, *, session: Session, account_id: str, currency: str = "SEK", institution: str = "SEB"
    ) -> Self:
        """Return existing account or create it on‑the‑fly inside *session*."""
        acct: Self | None = session.query(cls).filter_by(name=account_id).one_or_none()
        if acct is None:
            acct = cls(name=account_id, currency=currency, institution=institution)
            session.add(acct)
        return acct


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    payee: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    tx_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    raw: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)

    account: Mapped[Account] = relationship(back_populates="transactions")

    # Helper to create hash ------------------------------------------------
    @staticmethod
    def calc_hash(
        account: str, date: str, payee: str, amount: float, currency: str
    ) -> str:  # noqa: D401
        h = hashlib.sha256()
        h.update(f"{account}|{date}|{payee}|{amount}|{currency}".encode())
        return h.hexdigest()
