-- Migration: Add user preferences (language and currency)
-- Date: 2025-10-03

-- Add new columns to users table
ALTER TABLE users 
ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en',
ADD COLUMN preferred_currency VARCHAR(10) DEFAULT 'USD';

-- Update existing users to have default values
UPDATE users 
SET preferred_language = 'en', preferred_currency = 'USD' 
WHERE preferred_language IS NULL OR preferred_currency IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN users.preferred_language IS 'User preferred language code (en, ru, etc.)';
COMMENT ON COLUMN users.preferred_currency IS 'User preferred currency code (USD, EUR, RUB, etc.)';

