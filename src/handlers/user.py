from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from src.models.user import User
from src.models.category import Category
from src.database.init_db import create_default_categories
from src.utils.translations import get_translation, format_amount
from src.utils.balance_calculator import get_balance_calculator
from .base import BaseHandler

class UserHandler(BaseHandler):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Default handle method - not used in this handler"""
        pass
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command for both users and groups"""
        user_data = self.get_context_from_update(update)
        
        # Check if user/group exists
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        if not user:
            # Create new user/group
            user = User(**user_data)
            # Set preferred language
            if user_data.get('language_code') and user_data['language_code'].startswith('ru'):
                user.preferred_language = "ru"
            else:
                user.preferred_language = "en"
            user.preferred_currency = "USD"  # Default currency
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            # Create default categories
            create_default_categories(self.db, user.id)
        
        language = user.preferred_language if user else "en"
        
        if user_data['is_group']:
            menu_message = get_translation("group_management_menu", language)
            # If group menu message is empty, use a default message
            if not menu_message.strip():
                menu_message = "🤖 Group Expense Tracker"
        else:
            menu_message = get_translation("main_menu", language)
            # If menu message is empty, use a default message
            if not menu_message.strip():
                menu_message = "🤖 Expense Tracker Bot"
        
        if user_data['is_group']:
            keyboard = [
                [InlineKeyboardButton(
                    get_translation("add_expense", language), 
                    callback_data="add_expense"
                )],
                [InlineKeyboardButton(
                    get_translation("add_income", language), 
                    callback_data="add_income"
                )],
                [InlineKeyboardButton(
                    get_translation("manage_transactions", language), 
                    callback_data="manage_transactions"
                )],
                [InlineKeyboardButton(
                    get_translation("view_reports", language), 
                    callback_data="view_reports"
                )],
                [InlineKeyboardButton(
                    get_translation("settings", language), 
                    callback_data="settings"
                )]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton(
                    get_translation("add_expense", language), 
                    callback_data="add_expense"
                )],
                [InlineKeyboardButton(
                    get_translation("add_income", language), 
                    callback_data="add_income"
                )],
                [InlineKeyboardButton(
                    get_translation("manage_transactions", language), 
                    callback_data="manage_transactions"
                )],
                [InlineKeyboardButton(
                    get_translation("view_reports", language), 
                    callback_data="view_reports"
                )],
                [InlineKeyboardButton(
                    get_translation("settings", language), 
                    callback_data="settings"
                )]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(menu_message, reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text(menu_message, reply_markup=reply_markup)
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        language = user.preferred_language if user else "en"
        help_text = get_translation("help_text", language)
        
        await update.message.reply_text(help_text)
    
    async def handle_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /balance command"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        if not user:
            await update.message.reply_text(get_translation("user_not_found", "en"))
            return
        
        # No need to check for group context - unified logic handles both
        
        # Calculate balance using new calculator
        language = user.preferred_language if user else "en"
        base_currency = user.preferred_currency or "USD"
        
        balance_calculator = get_balance_calculator(self.db)
        balance_message = await balance_calculator.format_balance_message(
            user.id, base_currency, language
        )
        
        await update.message.reply_text(balance_message)
