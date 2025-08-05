# ──────────────────────────────────────────────────────────────────────────────
# alembic/env.py  (minimal offline/online run support)
# ──────────────────────────────────────────────────────────────────────────────
"""Alembic env; generated tables from ORM metadata."""
from __future__ import annotations

# ruff: noqa: I001

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context  # type: ignore[attr-defined]
from budget_app.config import get_settings
from budget_app.models import Base  # noqa: F401  (needed for metadata)

# Interpret the config file for Python logging.
config = context.config
fileConfig(config.config_file_name)

db_url = get_settings().DATABASE_URL
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:  # pragma: no cover
    context.configure(url=db_url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:  # pragma: no cover
    connectable = engine_from_config(
        config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
