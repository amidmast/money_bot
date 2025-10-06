# Database Migrations

This document describes all database migrations applied to the Expense Tracker Bot.

## Migration History

### Migration 1: User Preferences (2025-10-03)
**Purpose**: Add language and currency preferences for users

**Changes**:
- Added `preferred_language` column to `users` table (VARCHAR(10), default: 'en')
- Added `preferred_currency` column to `users` table (VARCHAR(10), default: 'USD')
- Updated existing users with default values

**SQL**:
```sql
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(10) DEFAULT 'en',
ADD COLUMN IF NOT EXISTS preferred_currency VARCHAR(10) DEFAULT 'USD';

UPDATE users 
SET preferred_language = 'en', preferred_currency = 'USD' 
WHERE preferred_language IS NULL OR preferred_currency IS NULL;
```

### Migration 2: Transaction Currency Support (2025-10-03)
**Purpose**: Add currency field to transactions for multi-currency support

**Changes**:
- Added `currency` column to `transactions` table (VARCHAR(10), default: 'USD')
- Updated existing transactions with default currency

**SQL**:
```sql
ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'USD';

UPDATE transactions 
SET currency = 'USD' 
WHERE currency IS NULL;
```

### Migration 3: Exchange Rates Table (2025-10-03)
**Purpose**: Create table for storing exchange rates between currencies

**Changes**:
- Created `exchange_rates` table with columns:
  - `id` (VARCHAR, PRIMARY KEY) - Format: "USD_TO_EUR"
  - `from_currency` (VARCHAR) - Source currency
  - `to_currency` (VARCHAR) - Target currency
  - `rate` (FLOAT) - Exchange rate
  - `last_updated` (TIMESTAMP) - Last update time

**SQL**:
```sql
CREATE TABLE IF NOT EXISTS exchange_rates (
    id VARCHAR PRIMARY KEY,
    from_currency VARCHAR NOT NULL,
    to_currency VARCHAR NOT NULL,
    rate FLOAT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Running Migrations

All migrations are automatically applied when running:

```bash
python setup_database.py
```

Or in Docker:

```bash
docker compose exec bot python setup_database.py
```

## Supported Features After Migrations

### Languages
- English (en)
- Russian (ru)

### Currencies
- **Fiat**: USD, UAH (Ukrainian Hryvnia)
- **Crypto**: USDT (Tether), ATOM (Cosmos)

### Exchange Rate Sources
- **Fiat currencies**: ExchangeRate-API
- **Cryptocurrencies**: CoinGecko API
- **Update frequency**: Every hour
- **Caching**: Database storage with timestamp tracking

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    username VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    language_code VARCHAR,
    preferred_language VARCHAR(10) DEFAULT 'en',
    preferred_currency VARCHAR(10) DEFAULT 'USD',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    description TEXT,
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id INTEGER REFERENCES users(id),
    category_id INTEGER REFERENCES categories(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Exchange Rates Table
```sql
CREATE TABLE exchange_rates (
    id VARCHAR PRIMARY KEY,
    from_currency VARCHAR NOT NULL,
    to_currency VARCHAR NOT NULL,
    rate FLOAT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Notes

- All migrations are idempotent (safe to run multiple times)
- Default values are applied to existing data
- Foreign key constraints are maintained
- Indexes are preserved for performance
