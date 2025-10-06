"""
Balance calculation with multi-currency support
"""

import asyncio
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.transaction import Transaction
from src.models.category import Category, CategoryType
from src.utils.exchange_rates import exchange_manager
from src.utils.translations import get_currency_symbol, SUPPORTED_CURRENCIES

class BalanceCalculator:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def calculate_user_balance(self, user_id: int, base_currency: str = "USD") -> Dict:
        """Calculate user's balance in base currency"""
        # Get personal transactions
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).all()
        
        if not transactions:
            return {
                "total_income": 0.0,
                "total_expenses": 0.0,
                "balance": 0.0,
                "currency": base_currency,
                "currency_breakdown": {}
            }
        
        # Group transactions by currency
        currency_totals = {}
        currency_breakdown = {}
        
        for transaction in transactions:
            currency = transaction.currency or "USD"
            
            if currency not in currency_totals:
                currency_totals[currency] = {"income": 0.0, "expenses": 0.0}
            
            # Convert to base currency
            amount_in_base = await exchange_manager.convert_amount(
                float(transaction.amount), 
                currency, 
                base_currency
            )
            
            # Determine if transaction is income or expense
            is_income = transaction.is_income
            
            if is_income:
                currency_totals[currency]["income"] += float(transaction.amount)
            else:
                currency_totals[currency]["expenses"] += float(transaction.amount)
            
            # Store breakdown by currency
            if currency not in currency_breakdown:
                currency_breakdown[currency] = {
                    "income": 0.0,
                    "expenses": 0.0,
                    "balance": 0.0,
                    "income_in_base": 0.0,
                    "expenses_in_base": 0.0,
                    "balance_in_base": 0.0
                }
            
            if is_income:
                currency_breakdown[currency]["income"] += float(transaction.amount)
                currency_breakdown[currency]["income_in_base"] += amount_in_base
            else:
                currency_breakdown[currency]["expenses"] += float(transaction.amount)
                currency_breakdown[currency]["expenses_in_base"] += amount_in_base
        
        # Calculate totals in base currency
        total_income = 0.0
        total_expenses = 0.0
        
        for currency, totals in currency_totals.items():
            income_in_base = await exchange_manager.convert_amount(
                totals["income"], currency, base_currency
            )
            expenses_in_base = await exchange_manager.convert_amount(
                totals["expenses"], currency, base_currency
            )
            
            total_income += income_in_base
            total_expenses += expenses_in_base
            
            # Update currency breakdown
            currency_breakdown[currency]["balance"] = totals["income"] - totals["expenses"]
            currency_breakdown[currency]["balance_in_base"] = income_in_base - expenses_in_base
        
        balance = total_income - total_expenses
        
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": balance,
            "currency": base_currency,
            "currency_breakdown": currency_breakdown
        }
    
    async def get_balance_by_currency(self, user_id: int) -> Dict[str, Dict]:
        """Get balance breakdown by each currency"""
        # Get personal transactions grouped by currency
        currency_data = self.db.query(
            Transaction.currency,
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('transaction_count')
        ).filter(
            Transaction.user_id == user_id
        ).group_by(Transaction.currency).all()
        
        result = {}
        
        for currency, total_amount, transaction_count in currency_data:
            currency = currency or "USD"
            
            # Get income and expenses for this currency
            income = self.db.query(func.sum(Transaction.amount)).join(Category).filter(
                Transaction.user_id == user_id,
                Transaction.currency == currency,
                Category.category_type == CategoryType.INCOME
            ).scalar() or 0
            
            expenses = self.db.query(func.sum(Transaction.amount)).join(Category).filter(
                Transaction.user_id == user_id,
                Transaction.currency == currency,
                Category.category_type == CategoryType.EXPENSE
            ).scalar() or 0
            
            result[currency] = {
                "total_amount": float(total_amount),
                "income": float(income),
                "expenses": float(expenses),
                "balance": float(income - expenses),
                "transaction_count": transaction_count
            }
        
        return result
    
    async def format_balance_message(self, user_id: int, base_currency: str = "USD", language: str = "en") -> str:
        """Format balance message with multi-currency support"""
        from src.utils.translations import get_translation
        
        balance_data = await self.calculate_user_balance(user_id, base_currency)
        currency_breakdown = await self.get_balance_by_currency(user_id)
        
        # Format main balance
        balance_symbol = get_currency_symbol(base_currency)
        balance_text = f"{balance_symbol} {balance_data['balance']:.2f}"
        
        if balance_data['balance'] >= 0:
            balance_emoji = "💰"
        else:
            balance_emoji = "💸"
        
        message = f"{balance_emoji} **{get_translation('balance', language)}**: {balance_text}\n\n"
        
        # Add currency breakdown if multiple currencies
        if len(currency_breakdown) > 1:
            message += f"📊 **{get_translation('currency_breakdown', language)}**:\n"
            
            for currency, data in currency_breakdown.items():
                symbol = get_currency_symbol(currency)
                message += f"• {symbol} {data['balance']:.2f} ({data['transaction_count']} {get_translation('transactions', language)})\n"
        
        return message

# Convenience function
def get_balance_calculator(db_session: Session) -> BalanceCalculator:
    """Get a BalanceCalculator instance"""
    return BalanceCalculator(db_session)