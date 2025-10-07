#!/usr/bin/env python3
"""
Simple entry point to run all required database migrations on a fresh or existing DB.

Usage inside container:
  python migrations.py
"""

import sys
import os
import asyncio

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.connection import engine
from src.models.base import Base
from setup_database import create_default_categories, initialize_exchange_rates
from sqlalchemy import text

# Import all models so metadata is populated
from src.models.user import User  # noqa: F401
from src.models.category import Category  # noqa: F401
from src.models.transaction import Transaction  # noqa: F401
from src.models.exchange_rates import ExchangeRate  # noqa: F401


def _run_sql_migrations():
    """Execute all .sql files from migrations/ in sorted order (idempotent)."""
    migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    if not os.path.isdir(migrations_dir):
        print("No migrations directory found; skipping SQL migrations")
        return

    sql_files = [f for f in os.listdir(migrations_dir) if f.endswith('.sql')]
    sql_files.sort()
    if not sql_files:
        print("No .sql migration files found; skipping")
        return

    print("Applying SQL migrations:")
    from src.database.connection import engine as _engine
    with _engine.connect() as conn:
        for fname in sql_files:
            path = os.path.join(migrations_dir, fname)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    sql_text = f.read()
                if not sql_text.strip():
                    continue
                print(f"  - {fname}")
                conn.execute(text(sql_text))
                conn.commit()
            except Exception as e:
                print(f"    ⚠ {fname}: {e}")

async def main():
    # 1) Ensure base tables exist via SQLAlchemy models
    Base.metadata.create_all(bind=engine)

    # 2) Apply SQL migrations (idempotent) from migrations/*.sql
    _run_sql_migrations()

    # 3) Seed defaults (idempotent)
    create_default_categories()

    # 4) Initialize exchange rates
    await initialize_exchange_rates()

    print("✅ Migrations finished successfully")


if __name__ == "__main__":
    asyncio.run(main())


