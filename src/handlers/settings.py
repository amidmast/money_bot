from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from src.models.user import User
from src.models.category import Category, CategoryType
from src.utils.translations import (
    get_translation, 
    SUPPORTED_LANGUAGES, 
    SUPPORTED_CURRENCIES,
    get_currency_symbol
)
from .base import BaseHandler

class SettingsHandler(BaseHandler):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Default handle method - not used in this handler"""
        pass
    
    async def handle_settings_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle settings menu"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        
        language = user.preferred_language if user else "en"
        
        keyboard = [
            [InlineKeyboardButton(
                get_translation("language_settings", language),
                callback_data="language_settings"
            )],
            [InlineKeyboardButton(
                get_translation("currency_settings", language),
                callback_data="currency_settings"
            )],
            [InlineKeyboardButton(
                get_translation("manage_categories", language),
                callback_data="manage_categories"
            )],
            [InlineKeyboardButton(
                get_translation("balance_settings", language),
                callback_data="balance_settings"
            )],
            [InlineKeyboardButton(
                get_translation("back_to_main", language),
                callback_data="main_menu"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        menu_text = get_translation("settings_menu", language)
        if not menu_text.strip():
            menu_text = "⚙️ Settings"
        
        await update.callback_query.edit_message_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_language_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle language settings menu"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        
        current_language = user.preferred_language or "en"
        
        keyboard = []
        for lang_code, lang_name in SUPPORTED_LANGUAGES.items():
            # Add checkmark for current language
            button_text = f"{'✅' if lang_code == current_language else '⚪'} {lang_name}"
            keyboard.append([InlineKeyboardButton(
                button_text,
                callback_data=f"set_language_{lang_code}"
            )])
        
        keyboard.append([InlineKeyboardButton(
            get_translation("back", current_language),
            callback_data="settings"
        )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            get_translation("select_language", current_language),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_set_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle language selection"""
        callback_data = update.callback_query.data
        language_code = callback_data.split("_")[-1]
        
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        
        # Update user's preferred language
        user.preferred_language = language_code
        self.db.commit()
        
        language_name = SUPPORTED_LANGUAGES.get(language_code, language_code)
        
        await update.callback_query.answer(
            get_translation("language_changed", language_code, language_name=language_name)
        )
        
        # Return to settings menu with new language
        await self.handle_settings_menu(update, context)
    
    async def handle_currency_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle currency settings menu"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        
        current_language = user.preferred_language or "en"
        current_currency = user.preferred_currency or "USD"
        
        keyboard = []
        for currency_code, currency_info in SUPPORTED_CURRENCIES.items():
            # Add checkmark for current currency
            button_text = f"{'✅' if currency_code == current_currency else '⚪'} {currency_code} - {currency_info['name']}"
            keyboard.append([InlineKeyboardButton(
                button_text,
                callback_data=f"set_currency_{currency_code}"
            )])
        
        keyboard.append([InlineKeyboardButton(
            get_translation("back", current_language),
            callback_data="settings"
        )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            get_translation("select_currency", current_language),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_balance_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Choose primary income category for balance deductions"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        language = user.preferred_language or "en"
        categories = self.db.query(Category).filter(
            Category.user_id == user.id,
            Category.category_type == CategoryType.INCOME,
            Category.is_active == True
        ).all()
        keyboard = []
        for c in categories:
            checked = '✅' if user.primary_income_category_id == c.id else '⚪'
            keyboard.append([InlineKeyboardButton(
                f"{checked} {c.icon} {c.get_name(language)}",
                callback_data=f"set_primary_income_{c.id}"
            )])
        keyboard.append([InlineKeyboardButton(get_translation("back", language), callback_data="settings")])
        await update.callback_query.edit_message_text(
            get_translation("select_primary_income_category", language),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    async def handle_set_primary_income(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        callback_data = update.callback_query.data
        category_id = int(callback_data.split("_")[-1])
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        user.primary_income_category_id = category_id
        self.db.commit()
        await self.handle_balance_settings(update, context)
    
    async def handle_set_currency(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle currency selection"""
        callback_data = update.callback_query.data
        currency_code = callback_data.split("_")[-1]
        
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        
        # Update user's preferred currency
        user.preferred_currency = currency_code
        self.db.commit()
        
        currency_info = SUPPORTED_CURRENCIES.get(currency_code, {})
        currency_name = currency_info.get("name", currency_code)
        language = user.preferred_language if user else "en"
        
        await update.callback_query.answer(
            get_translation("currency_changed", language, currency_name=currency_name)
        )
        
        # Return to settings menu
        await self.handle_settings_menu(update, context)

