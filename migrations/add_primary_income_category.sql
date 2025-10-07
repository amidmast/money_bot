ALTER TABLE users
ADD COLUMN IF NOT EXISTS primary_income_category_id INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_users_primary_income_category'
          AND table_name = 'users'
    ) THEN
        ALTER TABLE users
        ADD CONSTRAINT fk_users_primary_income_category
        FOREIGN KEY (primary_income_category_id) REFERENCES categories(id);
    END IF;
END $$;
