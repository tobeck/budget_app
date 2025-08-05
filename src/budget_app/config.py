# ──────────────────────────────────────────────────────────────────────────────
# src/budget_app/config.py
# ──────────────────────────────────────────────────────────────────────────────
"""Runtime configuration (DB URL, etc.) via env vars or .env file."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+pysqlite:///./budget.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:  # pragma: no cover
    return Settings()
