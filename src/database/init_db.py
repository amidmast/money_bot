from sqlalchemy.orm import Session
from src.database.connection import engine, Base
from src.models import User, Category, Transaction
from sqlalchemy import inspect
from src.models.category import CategoryType

def create_tables():
    """Create all database tables"""
    # Ensure all model modules are imported so SQLAlchemy registers them on Base
    from src.models.user import User  # noqa: F401
    from src.models.category import Category  # noqa: F401
    from src.models.transaction import Transaction  # noqa: F401
    from src.models.exchange_rates import ExchangeRate  # noqa: F401
    inspector = inspect(engine)
    existing = set(inspector.get_table_names(schema='public'))
    # Create tables one by one if missing
    # Create in dependency-safe order: categories -> users -> transactions -> exchange_rates
    tables = [Category.__table__, User.__table__, Transaction.__table__, ExchangeRate.__table__]
    for table in tables:
        if table.name not in existing:
            try:
                print(f"Creating table: {table.name}...")
                table.create(bind=engine, checkfirst=False)
                print(f"  ✓ Created {table.name}")
            except Exception as e:
                print(f"  ⚠ Failed creating {table.name}: {e}")

def create_default_categories(db: Session, user_id: int):
    """Create default categories for a new user"""
    default_categories = [
        # Income categories
        {"name_en": "Salary", "name_ru": "Зарплата", "description_en": "Monthly salary", "description_ru": "Ежемесячная зарплата", "category_type": CategoryType.INCOME, "color": "#27ae60", "icon": "💰", "is_default": True},
        {"name_en": "Freelance", "name_ru": "Фриланс", "description_en": "Freelance work", "description_ru": "Фриланс работа", "category_type": CategoryType.INCOME, "color": "#2ecc71", "icon": "💼", "is_default": True},
        {"name_en": "Investment", "name_ru": "Инвестиции", "description_en": "Investment returns", "description_ru": "Доходы от инвестиций", "category_type": CategoryType.INCOME, "color": "#16a085", "icon": "📈", "is_default": True},
        {"name_en": "Other Income", "name_ru": "Прочие доходы", "description_en": "Other income sources", "description_ru": "Другие источники дохода", "category_type": CategoryType.INCOME, "color": "#1abc9c", "icon": "💵", "is_default": True},
        
        # Expense categories
        {"name_en": "Food & Dining", "name_ru": "Еда и рестораны", "description_en": "Restaurants, groceries", "description_ru": "Рестораны, продукты", "category_type": CategoryType.EXPENSE, "color": "#e74c3c", "icon": "🍽️", "is_default": True},
        {"name_en": "Transportation", "name_ru": "Транспорт", "description_en": "Gas, public transport", "description_ru": "Бензин, общественный транспорт", "category_type": CategoryType.EXPENSE, "color": "#f39c12", "icon": "🚗", "is_default": True},
        {"name_en": "Shopping", "name_ru": "Покупки", "description_en": "Clothes, electronics", "description_ru": "Одежда, электроника", "category_type": CategoryType.EXPENSE, "color": "#e67e22", "icon": "🛍️", "is_default": True},
        {"name_en": "Entertainment", "name_ru": "Развлечения", "description_en": "Movies, games, hobbies", "description_ru": "Фильмы, игры, хобби", "category_type": CategoryType.EXPENSE, "color": "#9b59b6", "icon": "🎬", "is_default": True},
        {"name_en": "Bills & Utilities", "name_ru": "Счета и коммунальные услуги", "description_en": "Electricity, water, internet", "description_ru": "Электричество, вода, интернет", "category_type": CategoryType.EXPENSE, "color": "#34495e", "icon": "⚡", "is_default": True},
        {"name_en": "Healthcare", "name_ru": "Здоровье", "description_en": "Medical expenses", "description_ru": "Медицинские расходы", "category_type": CategoryType.EXPENSE, "color": "#e91e63", "icon": "🏥", "is_default": True},
        {"name_en": "Education", "name_ru": "Образование", "description_en": "Courses, books", "description_ru": "Курсы, книги", "category_type": CategoryType.EXPENSE, "color": "#3498db", "icon": "📚", "is_default": True},
        {"name_en": "Other Expenses", "name_ru": "Прочие расходы", "description_en": "Miscellaneous expenses", "description_ru": "Разные расходы", "category_type": CategoryType.EXPENSE, "color": "#95a5a6", "icon": "📝", "is_default": True},
    ]
    
    for cat_data in default_categories:
        category = Category(user_id=user_id, **cat_data)
        db.add(category)
    
    db.commit()

def init_database():
    """Initialize database with tables and default data"""
    create_tables()
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
