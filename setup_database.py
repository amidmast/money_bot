#!/usr/bin/env python3
"""
Database setup script for Expense Tracker Bot
Run this script to initialize the database with tables and default data
"""

import sys
import os
import asyncio

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.init_db import init_database
from src.database.connection import engine
from src.utils.exchange_rates import exchange_manager
from sqlalchemy import text

def run_migrations():
    """Run database migrations"""
    print("Running database migrations...")
    
    with engine.connect() as conn:
        # Migration 1: Add user preferences
        print("  - Adding user preferences (language, currency)...")
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(10) DEFAULT 'en',
                ADD COLUMN IF NOT EXISTS preferred_currency VARCHAR(10) DEFAULT 'USD';
            """))
            conn.execute(text("""
                UPDATE users 
                SET preferred_language = 'en', preferred_currency = 'USD' 
                WHERE preferred_language IS NULL OR preferred_currency IS NULL;
            """))
            conn.commit()
            print("    ✓ User preferences added")
        except Exception as e:
            print(f"    ⚠ User preferences migration: {e}")
        
        # Migration 2: Add currency to transactions
        print("  - Adding currency field to transactions...")
        try:
            conn.execute(text("""
                ALTER TABLE transactions 
                ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'USD';
            """))
            conn.execute(text("""
                UPDATE transactions 
                SET currency = 'USD' 
                WHERE currency IS NULL;
            """))
            conn.commit()
            print("    ✓ Currency field added to transactions")
        except Exception as e:
            print(f"    ⚠ Transactions currency migration: {e}")
        
        # Migration 3: Create exchange rates table
        print("  - Creating exchange rates table...")
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS exchange_rates (
                    id VARCHAR PRIMARY KEY,
                    from_currency VARCHAR NOT NULL,
                    to_currency VARCHAR NOT NULL,
                    rate FLOAT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.commit()
            print("    ✓ Exchange rates table created")
        except Exception as e:
            print(f"    ⚠ Exchange rates table: {e}")
        
        # Migration 4: Add multilingual support to categories
        print("  - Adding multilingual support to categories...")
        try:
            # Check if old columns exist and migrate data
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'categories' AND column_name = 'name';
            """)).fetchone()
            
            if result:  # Old columns exist, need to migrate
                # Add new columns for multilingual support
                conn.execute(text("""
                    ALTER TABLE categories 
                    ADD COLUMN IF NOT EXISTS name_en VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS name_ru VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS description_en TEXT,
                    ADD COLUMN IF NOT EXISTS description_ru TEXT;
                """))
                
                # Migrate existing category names to both languages
                conn.execute(text("""
                    UPDATE categories 
                    SET name_en = name, name_ru = name
                    WHERE name_en IS NULL OR name_ru IS NULL;
                """))
                
                # Make new columns NOT NULL after migration
                conn.execute(text("""
                    ALTER TABLE categories 
                    ALTER COLUMN name_en SET NOT NULL,
                    ALTER COLUMN name_ru SET NOT NULL;
                """))
                
                # Drop old columns
                conn.execute(text("""
                    ALTER TABLE categories 
                    DROP COLUMN IF EXISTS name,
                    DROP COLUMN IF EXISTS description;
                """))
            else:
                # New schema, just ensure columns exist
                conn.execute(text("""
                    ALTER TABLE categories 
                    ADD COLUMN IF NOT EXISTS name_en VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS name_ru VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS description_en TEXT,
                    ADD COLUMN IF NOT EXISTS description_ru TEXT;
                """))
            
            conn.commit()
            print("    ✓ Categories multilingual support added")
        except Exception as e:
            print(f"    ⚠ Categories multilingual migration: {e}")
        
        # Migration 5: Create group tables
        print("  - Creating group tables...")
        try:
            # Create groups table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS groups (
                    id SERIAL PRIMARY KEY,
                    telegram_chat_id BIGINT UNIQUE NOT NULL,
                    title VARCHAR NOT NULL,
                    description TEXT,
                    group_type VARCHAR NOT NULL CHECK (group_type IN ('channel', 'group', 'supergroup')),
                    is_active BOOLEAN DEFAULT TRUE,
                    default_currency VARCHAR(10) DEFAULT 'USD' NOT NULL,
                    default_language VARCHAR(10) DEFAULT 'en' NOT NULL,
                    created_by_user_id INTEGER NOT NULL REFERENCES users(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create group_members table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS group_members (
                    id SERIAL PRIMARY KEY,
                    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    role VARCHAR NOT NULL DEFAULT 'member' CHECK (role IN ('admin', 'member', 'viewer')),
                    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    UNIQUE(group_id, user_id)
                );
            """))
            
            # Create group_categories table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS group_categories (
                    id SERIAL PRIMARY KEY,
                    name_en VARCHAR NOT NULL,
                    name_ru VARCHAR NOT NULL,
                    description_en TEXT,
                    description_ru TEXT,
                    category_type VARCHAR NOT NULL CHECK (category_type IN ('income', 'expense')),
                    color VARCHAR DEFAULT '#3498db',
                    icon VARCHAR,
                    is_default BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
                    created_by_user_id INTEGER NOT NULL REFERENCES users(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create group_transactions table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS group_transactions (
                    id SERIAL PRIMARY KEY,
                    amount NUMERIC(10,2) NOT NULL,
                    currency VARCHAR(10) DEFAULT 'USD' NOT NULL,
                    description TEXT,
                    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
                    category_id INTEGER NOT NULL REFERENCES group_categories(id) ON DELETE CASCADE,
                    created_by_user_id INTEGER NOT NULL REFERENCES users(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_groups_telegram_chat_id ON groups(telegram_chat_id);
                CREATE INDEX IF NOT EXISTS idx_group_members_group_id ON group_members(group_id);
                CREATE INDEX IF NOT EXISTS idx_group_members_user_id ON group_members(user_id);
                CREATE INDEX IF NOT EXISTS idx_group_categories_group_id ON group_categories(group_id);
                CREATE INDEX IF NOT EXISTS idx_group_transactions_group_id ON group_transactions(group_id);
                CREATE INDEX IF NOT EXISTS idx_group_transactions_category_id ON group_transactions(category_id);
                CREATE INDEX IF NOT EXISTS idx_group_transactions_created_by ON group_transactions(created_by_user_id);
            """))
            
            conn.commit()
            print("    ✓ Group tables created")
        except Exception as e:
            print(f"    ⚠ Group tables creation: {e}")
        
        # Migration 6: Fix telegram_chat_id column type
        print("  - Fixing telegram_chat_id column type...")
        try:
            # Check if groups table exists and has telegram_chat_id column
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'groups' AND column_name = 'telegram_chat_id'
            """)).fetchone()
            
            if result and result[1] == 'integer':
                # Change column type from INTEGER to BIGINT
                conn.execute(text("""
                    ALTER TABLE groups 
                    ALTER COLUMN telegram_chat_id TYPE BIGINT
                """))
                print("    ✓ telegram_chat_id column type changed to BIGINT")
            else:
                print("    ✓ telegram_chat_id column already has correct type or table doesn't exist")
            
            conn.commit()
        except Exception as e:
            print(f"    ⚠ telegram_chat_id column type fix: {e}")
        
        # Migration 7: Add comments for documentation
        print("  - Adding table comments...")
        try:
            conn.execute(text("""
                COMMENT ON COLUMN users.preferred_language IS 'User preferred language code (en, ru, etc.)';
                COMMENT ON COLUMN users.preferred_currency IS 'User preferred currency code (USD, EUR, RUB, USDT, ATOM, etc.)';
                COMMENT ON COLUMN transactions.currency IS 'Transaction currency code (USD, EUR, RUB, USDT, ATOM, etc.)';
                COMMENT ON COLUMN categories.name_en IS 'Category name in English';
                COMMENT ON COLUMN categories.name_ru IS 'Category name in Russian';
                COMMENT ON TABLE groups IS 'Groups/channels for shared expense tracking';
                COMMENT ON TABLE group_members IS 'Members of groups with their roles';
                COMMENT ON TABLE group_categories IS 'Categories for group transactions';
                COMMENT ON TABLE group_transactions IS 'Transactions within groups';
            """))
            conn.commit()
            print("    ✓ Table comments added")
        except Exception as e:
            print(f"    ⚠ Table comments: {e}")

        # Migration 8: Remove group tables and modify users table for group support
        print("  - Removing group tables and modifying users table...")
        try:
            # Drop group-related tables
            conn.execute(text("DROP TABLE IF EXISTS group_transactions CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS group_categories CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS group_members CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS groups CASCADE"))
            print("    ✓ Group tables dropped")
            
            # Add group-specific columns to users table
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS is_group BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS group_title VARCHAR(255),
                ADD COLUMN IF NOT EXISTS group_type VARCHAR(50)
            """))
            print("    ✓ Group columns added to users table")
            
            conn.commit()
        except Exception as e:
            print(f"    ⚠ Group tables removal: {e}")

        # Migration 9: Add primary_income_category_id to users
        print("  - Adding primary_income_category_id to users...")
        try:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS primary_income_category_id INTEGER REFERENCES categories(id)
            """))
            conn.commit()
            print("    ✓ primary_income_category_id added")
        except Exception as e:
            print(f"    ⚠ Add primary_income_category_id: {e}")

async def initialize_exchange_rates():
    """Initialize exchange rates with some default values"""
    print("Initializing exchange rates...")
    try:
        # Update a few key exchange rates
        await exchange_manager.update_all_rates()
        print("  ✓ Exchange rates initialized")
    except Exception as e:
        print(f"  ⚠ Exchange rates initialization: {e}")

def create_default_categories():
    """Create default categories with multilingual names"""
    print("Creating default categories...")
    try:
        from src.database.session import get_session
        from src.models.user import User
        with get_session() as session:
            from src.models.category import Category, CategoryType
            
            # Default expense categories
            default_expense_categories = [
                {"name_en": "Food & Dining", "name_ru": "Еда и рестораны", "icon": "🍽️"},
                {"name_en": "Transportation", "name_ru": "Транспорт", "icon": "🚗"},
                {"name_en": "Shopping", "name_ru": "Покупки", "icon": "🛍️"},
                {"name_en": "Entertainment", "name_ru": "Развлечения", "icon": "🎬"},
                {"name_en": "Bills & Utilities", "name_ru": "Счета и коммунальные услуги", "icon": "⚡"},
                {"name_en": "Healthcare", "name_ru": "Здоровье", "icon": "🏥"},
                {"name_en": "Education", "name_ru": "Образование", "icon": "📚"},
                {"name_en": "Other Expenses", "name_ru": "Прочие расходы", "icon": "📝"},
            ]
            
            # Default income categories
            default_income_categories = [
                {"name_en": "Salary", "name_ru": "Зарплата", "icon": "💰"},
                {"name_en": "Freelance", "name_ru": "Фриланс", "icon": "💼"},
                {"name_en": "Investment", "name_ru": "Инвестиции", "icon": "📈"},
                {"name_en": "Other Income", "name_ru": "Прочие доходы", "icon": "💵"},
            ]
            
            # Create categories for all users
            users = session.query(User).all()
            for user in users:
                # Check if user already has categories
                existing_categories = session.query(Category).filter(Category.user_id == user.id).count()
                if existing_categories > 0:
                    continue
                
                # Create expense categories
                for cat_data in default_expense_categories:
                    category = Category(
                        name_en=cat_data["name_en"],
                        name_ru=cat_data["name_ru"],
                        category_type=CategoryType.EXPENSE,
                        user_id=user.id,
                        icon=cat_data["icon"],
                        is_default=True
                    )
                    session.add(category)
                
                # Create income categories
                for cat_data in default_income_categories:
                    category = Category(
                        name_en=cat_data["name_en"],
                        name_ru=cat_data["name_ru"],
                        category_type=CategoryType.INCOME,
                        user_id=user.id,
                        icon=cat_data["icon"],
                        is_default=True
                    )
                    session.add(category)
            
            session.commit()
            print("  ✓ Default categories created")
    except Exception as e:
        print(f"  ⚠ Default categories creation: {e}")

async def main():
    """Main setup function"""
    print("🚀 Setting up Expense Tracker Bot database...")
    print()
    
    # Initialize database tables
    print("1. Initializing database tables...")
    init_database()
    print("   ✓ Database tables created")
    print()
    
    # Run migrations
    print("2. Running migrations...")
    run_migrations()
    print()
    
    # Create default categories
    print("3. Creating default categories...")
    create_default_categories()
    print()
    
    # Initialize exchange rates
    print("4. Initializing exchange rates...")
    await initialize_exchange_rates()
    print()
    
    print("✅ Database setup completed successfully!")
    print()
    print("📊 Database includes:")
    print("   • Users table with language/currency preferences")
    print("   • Categories table with default categories")
    print("   • Transactions table with currency support")
    print("   • Exchange rates table for currency conversion")
    print("   • All necessary indexes and constraints")
    print()
    print("🌐 Supported languages: English, Russian")
    print("💱 Supported currencies: USD, UAH, USDT, ATOM")
    print()
    print("🎉 Your bot is ready to use!")

if __name__ == "__main__":
    asyncio.run(main())
