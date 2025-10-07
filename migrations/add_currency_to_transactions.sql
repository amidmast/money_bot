-- Migration: Add currency field to transactions table
-- Date: 2025-10-03

-- Add currency column to transactions table
ALTER TABLE transactions 
ADD COLUMN currency VARCHAR(10) DEFAULT 'USD';

-- Update existing transactions to have default currency
UPDATE transactions 
SET currency = 'USD' 
WHERE currency IS NULL;

-- Add comment for documentation
COMMENT ON COLUMN transactions.currency IS 'Transaction currency code (USD, EUR, USDT, ATOM, etc.)';
