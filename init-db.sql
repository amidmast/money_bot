-- Initialize database for Expense Tracker Bot
-- This script runs when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist (handled by POSTGRES_DB env var)
-- Create user if it doesn't exist (handled by POSTGRES_USER env var)

-- Grant necessary privileges
GRANT ALL PRIVILEGES ON DATABASE expense_tracker TO expense_user;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Expense Tracker Bot database initialized successfully';
END $$;

