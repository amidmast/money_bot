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
from setup_database import run_migrations, create_default_categories, initialize_exchange_rates

# Import all models so metadata is populated
from src.models.user import User  # noqa: F401
from src.models.category import Category  # noqa: F401
from src.models.transaction import Transaction  # noqa: F401
from src.models.exchange_rates import ExchangeRate  # noqa: F401


async def main():
    # 1) Ensure base tables exist via SQLAlchemy models
    Base.metadata.create_all(bind=engine)

    # 2) Apply SQL migrations (idempotent)
    run_migrations()

    # 3) Seed defaults (idempotent)
    create_default_categories()

    # 4) Initialize exchange rates
    await initialize_exchange_rates()

    print("✅ Migrations finished successfully")


if __name__ == "__main__":
    asyncio.run(main())


