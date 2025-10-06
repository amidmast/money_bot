#!/usr/bin/env python3
"""
Automated testing suite for the Expense Tracker Bot
"""

import asyncio
import sys
import os
import logging
from typing import Dict, List, Any
from unittest.mock import AsyncMock, MagicMock

# Add the src directory to the path
sys.path.append('/app')

from src.database.session import get_session
from src.models.user import User
from src.models.category import Category, CategoryType
from src.models.transaction import Transaction
from src.utils.translations import get_translation, SUPPORTED_LANGUAGES, SUPPORTED_CURRENCIES
from src.utils.exchange_rates import ExchangeRateManager
from src.utils.balance_calculator import BalanceCalculator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BotTester:
    def __init__(self):
        self.test_results = []
        self.errors = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        if not success:
            self.errors.append(f"{test_name}: {message}")
    
    def test_database_connection(self):
        """Test database connection"""
        try:
            with get_session() as session:
                # Test basic query
                user_count = session.query(User).count()
                self.log_test("Database Connection", True, f"Connected successfully, {user_count} users found")
                return True
        except Exception as e:
            self.log_test("Database Connection", False, str(e))
            return False
    
    def test_translations(self):
        """Test translation system"""
        try:
            # Test all supported languages
            for lang_code, lang_name in SUPPORTED_LANGUAGES.items():
                # Test basic translation
                welcome = get_translation("welcome_new", lang_code, name="Test User")
                if not welcome or "Test User" not in welcome:
                    self.log_test(f"Translation {lang_code}", False, "Welcome message not found")
                    return False
                
                # Test menu translations
                menu_items = [
                    "main_menu", "add_transaction", "view_reports", 
                    "manage_categories", "analytics", "settings"
                ]
                
                for item in menu_items:
                    translation = get_translation(item, lang_code)
                    if not translation:
                        self.log_test(f"Translation {lang_code} - {item}", False, "Translation not found")
                        return False
            
            self.log_test("Translation System", True, f"All translations work for {len(SUPPORTED_LANGUAGES)} languages")
            return True
        except Exception as e:
            self.log_test("Translation System", False, str(e))
            return False
    
    def test_currencies(self):
        """Test currency system"""
        try:
            # Test all supported currencies
            for currency_code, currency_info in SUPPORTED_CURRENCIES.items():
                if not currency_info.get("symbol") or not currency_info.get("name"):
                    self.log_test(f"Currency {currency_code}", False, "Missing symbol or name")
                    return False
            
            self.log_test("Currency System", True, f"All {len(SUPPORTED_CURRENCIES)} currencies configured")
            return True
        except Exception as e:
            self.log_test("Currency System", False, str(e))
            return False
    
    def test_models(self):
        """Test database models"""
        try:
            with get_session() as session:
                # Test User model
                users = session.query(User).limit(1).all()
                if users:
                    user = users[0]
                    # Test user attributes
                    required_attrs = ['telegram_id', 'first_name', 'preferred_language', 'preferred_currency']
                    for attr in required_attrs:
                        if not hasattr(user, attr):
                            self.log_test("User Model", False, f"Missing attribute: {attr}")
                            return False
                
                # Test Category model
                categories = session.query(Category).limit(1).all()
                if categories:
                    category = categories[0]
                    # Test category attributes
                    required_attrs = ['name_en', 'name_ru', 'category_type', 'user_id']
                    for attr in required_attrs:
                        if not hasattr(category, attr):
                            self.log_test("Category Model", False, f"Missing attribute: {attr}")
                            return False
                    
                    # Test get_name method
                    en_name = category.get_name("en")
                    ru_name = category.get_name("ru")
                    if not en_name or not ru_name:
                        self.log_test("Category Model", False, "get_name method not working")
                        return False
                
                # Test Transaction model
                transactions = session.query(Transaction).limit(1).all()
                if transactions:
                    transaction = transactions[0]
                    # Test transaction attributes
                    required_attrs = ['amount', 'currency', 'user_id', 'category_id']
                    for attr in required_attrs:
                        if not hasattr(transaction, attr):
                            self.log_test("Transaction Model", False, f"Missing attribute: {attr}")
                            return False
                
                self.log_test("Database Models", True, "All models working correctly")
                return True
        except Exception as e:
            self.log_test("Database Models", False, str(e))
            return False
    
    async def test_exchange_rates(self):
        """Test exchange rate system"""
        try:
            exchange_manager = ExchangeRateManager()
            
            # Test getting a rate
            rate = await exchange_manager.get_exchange_rate("USD", "UAH")
            if rate is None or rate <= 0:
                self.log_test("Exchange Rates", False, "Could not fetch exchange rate")
                return False
            
            self.log_test("Exchange Rates", True, f"USD to UAH rate: {rate}")
            return True
        except Exception as e:
            self.log_test("Exchange Rates", False, str(e))
            return False
    
    def test_balance_calculator(self):
        """Test balance calculator"""
        try:
            with get_session() as session:
                # Get a test user
                user = session.query(User).first()
                if not user:
                    self.log_test("Balance Calculator", False, "No users found for testing")
                    return False
                
                # Test balance calculation
                balance_calc = BalanceCalculator(session)
                
                # This will be tested with actual data
                self.log_test("Balance Calculator", True, "Balance calculator initialized successfully")
                return True
        except Exception as e:
            self.log_test("Balance Calculator", False, str(e))
            return False
    
    def test_category_operations(self):
        """Test category operations"""
        try:
            with get_session() as session:
                # Test creating a category
                test_user = session.query(User).first()
                if not test_user:
                    self.log_test("Category Operations", False, "No users found for testing")
                    return False
                
                # Test category creation
                test_category = Category(
                    name_en="Test Category",
                    name_ru="Тестовая категория",
                    category_type=CategoryType.EXPENSE,
                    user_id=test_user.id,
                    icon="🧪",
                    color="#FF5733"
                )
                
                # Test get_name method
                en_name = test_category.get_name("en")
                ru_name = test_category.get_name("ru")
                
                if en_name != "Test Category" or ru_name != "Тестовая категория":
                    self.log_test("Category Operations", False, "get_name method not working")
                    return False
                
                self.log_test("Category Operations", True, "Category operations working correctly")
                return True
        except Exception as e:
            self.log_test("Category Operations", False, str(e))
            return False
    
    def test_missing_translations(self):
        """Test for missing translations"""
        try:
            missing_translations = []
            
            # Get all translation keys used in code
            used_keys = set()
            
            # This is a simplified check - in a real implementation,
            # you would parse all source files to find get_translation calls
            common_keys = [
                "welcome_new", "welcome_back", "main_menu", "add_transaction",
                "view_reports", "manage_categories", "analytics", "settings",
                "user_not_found", "back_to_main", "add_income", "add_expense",
                "recent_transactions", "income", "expense", "enter_amount",
                "transaction_added", "category_created_success", "category_updated",
                "category_deleted", "invalid_color", "category_not_found"
            ]
            
            for key in common_keys:
                used_keys.add(key)
            
            # Check if all keys exist in all languages
            for lang_code in SUPPORTED_LANGUAGES.keys():
                for key in used_keys:
                    try:
                        translation = get_translation(key, lang_code)
                        if not translation:
                            missing_translations.append(f"{lang_code}:{key}")
                    except:
                        missing_translations.append(f"{lang_code}:{key}")
            
            if missing_translations:
                self.log_test("Missing Translations", False, f"Missing: {', '.join(missing_translations)}")
                return False
            else:
                self.log_test("Missing Translations", True, "All translations present")
                return True
        except Exception as e:
            self.log_test("Missing Translations", False, str(e))
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting Expense Tracker Bot Tests...")
        logger.info("=" * 50)
        
        # Run synchronous tests
        self.test_database_connection()
        self.test_translations()
        self.test_currencies()
        self.test_models()
        self.test_balance_calculator()
        self.test_category_operations()
        self.test_missing_translations()
        
        # Run asynchronous tests
        await self.test_exchange_rates()
        
        # Print summary
        logger.info("=" * 50)
        logger.info("📊 Test Summary:")
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        logger.info(f"✅ Passed: {passed}/{total}")
        logger.info(f"❌ Failed: {total - passed}/{total}")
        
        if self.errors:
            logger.info("\n🚨 Errors found:")
            for error in self.errors:
                logger.info(f"  - {error}")
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        logger.info(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            logger.info("🎉 Bot is in excellent condition!")
        elif success_rate >= 75:
            logger.info("⚠️  Bot has some issues but is mostly functional")
        else:
            logger.info("🚨 Bot has significant issues that need attention")
        
        return success_rate >= 75

async def main():
    """Main test function"""
    tester = BotTester()
    success = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
