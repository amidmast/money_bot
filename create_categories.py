#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

from src.database.session import get_session
from src.models.user import User
from src.models.category import Category, CategoryType

def create_default_categories():
    """Create default categories with multilingual names"""
    print("Creating default categories...")
    
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
    
    with get_session() as session:
        # Get all users
        users = session.query(User).all()
        print(f"Found {len(users)} users")
        
        for user in users:
            # Check if user already has categories
            existing_categories = session.query(Category).filter(Category.user_id == user.id).count()
            if existing_categories > 0:
                print(f"User {user.first_name} already has {existing_categories} categories, skipping...")
                continue
            
            print(f"Creating categories for user {user.first_name}...")
            
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
        print("✅ Default categories created successfully!")

if __name__ == "__main__":
    create_default_categories()
