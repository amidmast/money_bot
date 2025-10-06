from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from src.models.user import User
from src.models.category import Category, CategoryType
from src.models.transaction import Transaction
from src.utils.translations import get_translation, get_currency_symbol, SUPPORTED_CURRENCIES
from src.utils.keyboards import get_amount_keyboard
from .base import BaseHandler
from datetime import datetime, date
from typing import Optional

class TransactionHandler(BaseHandler):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Default handle method - not used in this handler"""
        pass
    
    async def handle_add_transaction(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle add transaction menu"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        
        language = user.preferred_language if user else "en"
        
        keyboard = [
            [InlineKeyboardButton(
                get_translation('recent_transactions', language), 
                callback_data="recent_transactions"
            )],
            [InlineKeyboardButton(
                get_translation('back_to_main', language), 
                callback_data="main_menu"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        menu_text = get_translation("add_transaction_menu", language)
        if not menu_text.strip():
            menu_text = "💰 Add Transaction"
        
        await update.callback_query.edit_message_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    def find_expense_category_by_text(self, update: Update, text: str) -> Optional[Category]:
        """Try to find an expense category mentioned in free-form text (localized)."""
        if not text:
            return None
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        if not user:
            return None
        language = user.preferred_language if user else "en"
        text_norm = text.lower()
        categories = self.db.query(Category).filter(
            Category.user_id == user.id,
            Category.category_type == CategoryType.EXPENSE,
            Category.is_active == True
        ).all()
        for category in categories:
            name = category.get_name(language).lower()
            if name and name in text_norm:
                return category
        return None

    async def start_expense_with_category_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE, category_id: int):
        """Start expense add flow directly with a selected category (message context)."""
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            if getattr(update, 'message', None):
                await update.message.reply_text("Category not found.")
            return

        context.user_data['selected_category_id'] = category_id
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        currency_code = user.preferred_currency if user else "USD"
        context.user_data['selected_currency'] = currency_code

        # Try to auto-set date from recognized text (today/yesterday in RU/EN/UA)
        text_src = context.user_data.get('voice_description', '')
        text_norm = (text_src or '').lower()
        selected_date = None
        today = datetime.now().date()
        if any(k in text_norm for k in ["сегодня", "today", "сьогодні"]):
            selected_date = today
        elif any(k in text_norm for k in ["вчера", "yesterday", "вчора"]):
            selected_date = today - timedelta(days=1)

        if selected_date is not None:
            # Jump straight to amount entry, preserving prefilled amount buffer if any
            context.user_data['selected_date'] = selected_date
            context.user_data['waiting_for_amount'] = True

            amount_display = context.user_data.get('amount_buffer', '') or '0'
            header_key = 'add_income' if category.category_type == CategoryType.INCOME else 'add_expense'
            amount_keyboard = get_amount_keyboard(language)
            await update.message.reply_text(
                f"{get_translation(header_key, language)}\n\n"
                f"{get_translation('category', language)}: {category.icon} {category.get_name(language)}\n"
                f"{get_translation('date', language)}: {selected_date.strftime('%d.%m.%Y')}\n\n"
                f"{get_translation('amount', language)}: **{amount_display}**",
                parse_mode='Markdown',
                reply_markup=amount_keyboard
            )
            return

        # Otherwise show date selection keyboard
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        keyboard = [
            [InlineKeyboardButton(
                f"📅 {get_translation('today', language)} ({today.strftime('%d.%m.%Y')})",
                callback_data="select_date_today"
            )],
            [InlineKeyboardButton(
                f"📅 {get_translation('yesterday', language)} ({yesterday.strftime('%d.%m.%Y')})",
                callback_data="select_date_yesterday"
            )],
            [InlineKeyboardButton(
                get_translation('custom_date', language),
                callback_data="select_date_custom"
            )],
            [InlineKeyboardButton(
                get_translation('back_to_main', language),
                callback_data="main_menu"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        header_key = 'add_income' if category.category_type == CategoryType.INCOME else 'add_expense'
        await update.message.reply_text(
            f"{get_translation(header_key, language)}\n\n"
            f"{get_translation('category', language)}: {category.icon} {category.get_name(language)}\n"
            f"{get_translation('select_date', language)}:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def create_transaction_direct(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *, category_id: int, amount: float, selected_date: date, description: str = ""):
        """Create a transaction immediately (used for auto-created voice transactions)."""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        if not user:
            if getattr(update, 'message', None):
                await update.message.reply_text("User not found. Use /start")
            return

        language = user.preferred_language if user else "en"
        currency_code = user.preferred_currency if user else "USD"

        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            if getattr(update, 'message', None):
                await update.message.reply_text("Category not found.")
            return

        transaction = Transaction(
            amount=amount,
            currency=currency_code,
            user_id=user.id,
            category_id=category.id,
            description=description or "",
            transaction_date=datetime.combine(selected_date, datetime.now().time())
        )
        self.db.add(transaction)
        self.db.commit()

        from src.utils.translations import get_currency_symbol
        currency_symbol = get_currency_symbol(currency_code)
        confirmation = (
            f"✅ {get_translation('transaction_added', language, currency_symbol=currency_symbol, amount=amount, category_icon=category.icon, category_name=category.get_name(language), transaction_type=get_translation('expense', language) if category.category_type == CategoryType.EXPENSE else get_translation('income', language))}\n\n"
        )

        keyboard = [[InlineKeyboardButton(get_translation('back_to_main', language), callback_data="main_menu")]]
        await update.message.reply_text(confirmation, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

        # Cleanup any temp state
        for key in ['voice_description', 'amount_buffer', 'selected_date', 'selected_currency', 'selected_category_id', 'waiting_for_amount', 'waiting_for_custom_date']:
            context.user_data.pop(key, None)
    
    async def handle_add_income(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle add income transaction"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        user_currency = user.preferred_currency if user else "USD"
        
        # Get income categories
        categories = self.db.query(Category).filter(
            Category.user_id == user.id,
            Category.category_type == CategoryType.INCOME,
            Category.is_active == True
        ).all()
        
        if not categories:
            await update.callback_query.edit_message_text(
                "❌ No income categories found. Please create some categories first.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="add_transaction")]])
            )
            return
        
        # Pre-calculate sums
        income_totals = dict(
            self.db.query(
                Transaction.category_id,
                func.coalesce(func.sum(Transaction.amount), 0)
            )
            .filter(
                Transaction.user_id == user.id,
                Transaction.currency == user_currency
            )
            .group_by(Transaction.category_id)
            .all()
        )

        # Total expenses (all-time) in user's currency
        total_expenses = self.db.query(func.coalesce(func.sum(Transaction.amount), 0)).join(Category).filter(
            Transaction.user_id == user.id,
            Transaction.currency == user_currency,
            Category.category_type == CategoryType.EXPENSE
        ).scalar() or 0

        primary_id = getattr(user, 'primary_income_category_id', None)

        keyboard = []
        for category in categories:
            localized_name = category.get_name(language)
            total_income_cat = float(income_totals.get(category.id, 0) or 0)
            if primary_id and category.id == primary_id:
                remaining = total_income_cat - float(total_expenses)
            else:
                remaining = total_income_cat
            remaining_int = int(round(remaining))
            button_text = f"{category.icon} {localized_name} [{user_currency} {remaining_int}]"
            keyboard.append([InlineKeyboardButton(
                button_text,
                callback_data=f"select_category_{category.id}"
            )])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            "💰 **Add Income**\n\nSelect a category:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_add_expense(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle add expense transaction"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        user_currency = user.preferred_currency if user else "USD"
        
        # Get expense categories
        categories = self.db.query(Category).filter(
            Category.user_id == user.id,
            Category.category_type == CategoryType.EXPENSE,
            Category.is_active == True
        ).all()
        
        if not categories:
            await update.callback_query.edit_message_text(
                "❌ No expense categories found. Please create some categories first.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="add_transaction")]])
            )
            return
        
        # Calculate per-category totals for current month in user's preferred currency
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        totals = dict(
            self.db.query(
                Transaction.category_id,
                func.coalesce(func.sum(Transaction.amount), 0)
            )
            .filter(
                Transaction.user_id == user.id,
                Transaction.transaction_date >= start_of_month,
                Transaction.currency == user_currency
            )
            .group_by(Transaction.category_id)
            .all()
        )

        keyboard = []
        for category in categories:
            localized_name = category.get_name(language)
            total_amount = totals.get(category.id, 0)
            # Show without decimals
            total_str = str(int(round(float(total_amount))))
            button_text = f"{localized_name} [{total_str} {user_currency}]"
            keyboard.append([InlineKeyboardButton(
                button_text,
                callback_data=f"select_category_{category.id}"
            )])
        keyboard.append([InlineKeyboardButton(
            get_translation('back_to_main', language), 
            callback_data="main_menu"
        )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if getattr(update, 'message', None):
            await update.message.reply_text(
                get_translation("select_category_for_expense", language),
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.callback_query.edit_message_text(
                get_translation("select_category_for_expense", language),
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def handle_select_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle category selection for transaction"""
        callback_data = update.callback_query.data
        category_id = int(callback_data.split("_")[-1])
        
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            await update.callback_query.answer("Category not found.")
            return
        
        context.user_data['selected_category_id'] = category_id
        # Get user's preferred language and currency
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        currency_code = user.preferred_currency if user else "USD"
        context.user_data['selected_currency'] = currency_code
        context.user_data['waiting_for_currency'] = False

        # If amount came from voice and no date keywords were recognized, default date to today and
        # go straight to amount input (skip date picker)
        voice_text = (context.user_data.get('voice_description') or '').lower()
        has_date_hint = any(k in voice_text for k in [
            'сегодня', 'today', 'сьогодні', 'вчера', 'yesterday', 'вчора'
        ])
        if context.user_data.get('amount_buffer') and not has_date_hint:
            selected_date = datetime.now().date()
            context.user_data['selected_date'] = selected_date
            context.user_data['waiting_for_amount'] = True

            amount_keyboard = get_amount_keyboard(language)

            header_key = 'add_income' if category.category_type == CategoryType.INCOME else 'add_expense'
            currency_info = SUPPORTED_CURRENCIES.get(currency_code, {})
            currency_symbol = currency_info.get('symbol', currency_code)
            amount_display = context.user_data.get('amount_buffer', '') or '0'

            await update.callback_query.edit_message_text(
                f"{get_translation(header_key, language)}\n\n"
                f"{get_translation('category', language)}: {category.icon} {category.get_name(language)}\n"
                f"Currency: {currency_symbol} {currency_code}\n"
                f"Date: {selected_date.strftime('%d.%m.%Y')}\n\n"
                f"{get_translation('amount', language)}: **{amount_display}**\n\n"
                f"Use the keyboard below to enter amount:",
                parse_mode='Markdown',
                reply_markup=amount_keyboard
            )
            return

        # Show date selection directly (no currency selection during add flow)
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        keyboard = [
            [InlineKeyboardButton(
                f"📅 {get_translation('today', language)} ({today.strftime('%d.%m.%Y')})",
                callback_data="select_date_today"
            )],
            [InlineKeyboardButton(
                f"📅 {get_translation('yesterday', language)} ({yesterday.strftime('%d.%m.%Y')})",
                callback_data="select_date_yesterday"
            )],
            [InlineKeyboardButton(
                get_translation('custom_date', language),
                callback_data="select_date_custom"
            )],
            [InlineKeyboardButton(
                get_translation('back_to_main', language),
                callback_data="main_menu"
            )]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        header_key = 'add_income' if category.category_type == CategoryType.INCOME else 'add_expense'
        currency_info = SUPPORTED_CURRENCIES.get(currency_code, {})
        currency_symbol = currency_info.get("symbol", currency_code)
        
        # Preserve voice-entered amount across category->date step
        if context.user_data.get('voice_amount') and not context.user_data.get('amount_buffer'):
            context.user_data['amount_buffer'] = context.user_data['voice_amount']

        await update.callback_query.edit_message_text(
            f"{get_translation(header_key, language)}\n\n"
            f"{get_translation('category', language)}: {category.icon} {category.get_name(language)}\n"
            f"{get_translation('select_date', language)}:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_select_currency(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle currency selection for transaction"""
        callback_data = update.callback_query.data
        currency_code = callback_data.split("_")[-1]
        
        category_id = context.user_data.get('selected_category_id')
        category = self.db.query(Category).filter(Category.id == category_id).first()
        
        if not category:
            await update.callback_query.answer("Category not found.")
            return
        
        # Store selected currency
        context.user_data['selected_currency'] = currency_code
        context.user_data['waiting_for_currency'] = False
        
        # Get user's preferred language
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        type_emoji = "💰" if category.category_type == CategoryType.INCOME else "💸"
        type_name = get_translation("income", language) if category.category_type == CategoryType.INCOME else get_translation("expense", language)
        currency_info = SUPPORTED_CURRENCIES.get(currency_code, {})
        currency_symbol = currency_info.get("symbol", currency_code)
        
        # Show date selection keyboard
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        keyboard = [
            [InlineKeyboardButton(
                f"📅 {get_translation('today', language)} ({today.strftime('%d.%m.%Y')})",
                callback_data="select_date_today"
            )],
            [InlineKeyboardButton(
                f"📅 {get_translation('yesterday', language)} ({yesterday.strftime('%d.%m.%Y')})",
                callback_data="select_date_yesterday"
            )],
            [InlineKeyboardButton(
                get_translation('custom_date', language),
                callback_data="select_date_custom"
            )],
            [InlineKeyboardButton(
                get_translation('back_to_main', language),
                callback_data="main_menu"
            )]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            f"{type_emoji} **Add {type_name}**\n\n"
            f"Category: {category.icon} {category.get_name(language)}\n"
            f"Currency: {currency_symbol} {currency_code}\n\n"
            f"📅 {get_translation('select_date', language)}:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def handle_select_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle date selection for transaction"""
        callback_data = update.callback_query.data
        
        # Get user's preferred language
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        if callback_data == "select_date_today":
            selected_date = datetime.now().date()
        elif callback_data == "select_date_yesterday":
            selected_date = datetime.now().date() - timedelta(days=1)
        elif callback_data == "select_date_custom":
            # Set flag to wait for custom date input
            context.user_data['waiting_for_custom_date'] = True
            context.user_data['waiting_for_amount'] = False
            
            await update.callback_query.edit_message_text(
                f"📅 {get_translation('enter_date', language)}\n\n"
                f"Format: DD.MM.YYYY (e.g., 15.03.2024)",
                parse_mode='Markdown'
            )
            return
        else:
            await update.callback_query.answer("Invalid date selection.")
            return
        
        # Store selected date
        context.user_data['selected_date'] = selected_date
        context.user_data['waiting_for_amount'] = True
        
        # Show amount input keyboard
        amount_keyboard = get_amount_keyboard(language)
        
        # Get category info for display
        category_id = context.user_data.get('selected_category_id')
        category = self.db.query(Category).filter(Category.id == category_id).first()
        currency_code = context.user_data.get('selected_currency')
        
        if category and currency_code:
            header_key = 'add_income' if category.category_type == CategoryType.INCOME else 'add_expense'
            currency_info = SUPPORTED_CURRENCIES.get(currency_code, {})
            currency_symbol = currency_info.get("symbol", currency_code)
            
            await update.callback_query.edit_message_text(
                f"{get_translation(header_key, language)}\n\n"
                f"{get_translation('category', language)}: {category.icon} {category.get_name(language)}\n"
                f"{get_translation('date', language)}: {selected_date.strftime('%d.%m.%Y')}\n\n"
                f"{get_translation('amount', language)}: **0**",
                parse_mode='Markdown',
                reply_markup=amount_keyboard
            )
    
    async def handle_custom_date_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle custom date input"""
        if not context.user_data.get('waiting_for_custom_date'):
            return
        
        # Get user's preferred language
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        date_text = update.message.text.strip()
        
        try:
            # Parse date in DD.MM.YYYY format
            selected_date = datetime.strptime(date_text, "%d.%m.%Y").date()
            
            # Check if date is not in the future
            today = datetime.now().date()
            if selected_date > today:
                await update.message.reply_text(
                    f"❌ {get_translation('future_date_not_allowed', language)}"
                )
                return
            
            # Store selected date
            context.user_data['selected_date'] = selected_date
            context.user_data['waiting_for_custom_date'] = False
            context.user_data['waiting_for_amount'] = True
            
            # Show amount input keyboard
            amount_keyboard = get_amount_keyboard(language)
            
            # Get category info for display
            category_id = context.user_data.get('selected_category_id')
            category = self.db.query(Category).filter(Category.id == category_id).first()
            currency_code = context.user_data.get('selected_currency')
            
            if category and currency_code:
                type_emoji = "💰" if category.category_type == CategoryType.INCOME else "💸"
                type_name = get_translation("income", language) if category.category_type == CategoryType.INCOME else get_translation("expense", language)
                currency_info = SUPPORTED_CURRENCIES.get(currency_code, {})
                currency_symbol = currency_info.get("symbol", currency_code)
                
                # Preserve pre-filled amount (e.g., from voice) if present
                amount_display = context.user_data.get('amount_buffer', '') or '0'
                await update.message.reply_text(
                    f"{type_emoji} **Add {type_name}**\n\n"
                    f"Category: {category.icon} {category.get_name(language)}\n"
                    f"Currency: {currency_symbol} {currency_code}\n"
                    f"Date: {selected_date.strftime('%d.%m.%Y')}\n\n"
                    f"Amount: **{amount_display}**\n\n"
                    f"Use the keyboard below to enter amount:",
                    parse_mode='Markdown',
                    reply_markup=amount_keyboard
                )
            
        except ValueError:
            await update.message.reply_text(
                f"❌ {get_translation('invalid_date_format', language)}"
            )
    
    async def handle_amount_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle amount input for transaction with buffer via callback queries"""
        if not context.user_data.get('waiting_for_amount'):
            return
        
        # Get user's preferred language
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        # Initialize amount buffer if not exists
        if 'amount_buffer' not in context.user_data:
            context.user_data['amount_buffer'] = ""
        
        callback_data = update.callback_query.data
        
        # Handle back button - return to date selection
        if callback_data == "amount_back":
            context.user_data.pop('waiting_for_amount', None)
            # Do not clear amount_buffer when navigating back from amount -> date
            
            # Show date selection keyboard again
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            keyboard = [
                [InlineKeyboardButton(
                    f"📅 {get_translation('today', language)} ({today.strftime('%d.%m.%Y')})",
                    callback_data="select_date_today"
                )],
                [InlineKeyboardButton(
                    f"📅 {get_translation('yesterday', language)} ({yesterday.strftime('%d.%m.%Y')})",
                    callback_data="select_date_yesterday"
                )],
                [InlineKeyboardButton(
                    get_translation('custom_date', language),
                    callback_data="select_date_custom"
                )],
                [InlineKeyboardButton(
                    get_translation('back_to_main', language),
                    callback_data="main_menu"
                )]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Get category info for display
            category_id = context.user_data.get('selected_category_id')
            category = self.db.query(Category).filter(Category.id == category_id).first()
            currency_code = context.user_data.get('selected_currency')
            
            if category and currency_code:
                header_key = 'add_income' if category.category_type == CategoryType.INCOME else 'add_expense'
                await update.callback_query.edit_message_text(
                    f"{get_translation(header_key, language)}\n\n"
                    f"{get_translation('category', language)}: {category.icon} {category.get_name(language)}\n\n"
                    f"{get_translation('select_date', language)}:",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            return
        
        # Handle enter button
        if callback_data == "amount_enter":
            if not context.user_data.get('amount_buffer'):
                await update.callback_query.answer(
                    get_translation("enter_amount", language),
                    show_alert=True
                )
                return
            
            try:
                amount = float(context.user_data['amount_buffer'].replace(',', '.'))
                if amount <= 0:
                    await update.callback_query.answer(
                        get_translation("invalid_amount", language),
                        show_alert=True
                    )
                    return
            except ValueError:
                await update.callback_query.answer(
                    get_translation("invalid_number", language),
                    show_alert=True
                )
                return
            
            # If currently editing a transaction's amount, update it
            if context.user_data.get('edit_mode') == 'amount' and context.user_data.get('editing_transaction_id'):
                tx_id = context.user_data['editing_transaction_id']
                transaction = self.db.query(Transaction).filter(
                    Transaction.id == tx_id,
                    Transaction.user_id == (self.db.query(User).filter(User.telegram_id == self.get_context_from_update(update)['telegram_id']).first()).id
                ).first()
                if not transaction:
                    await update.callback_query.answer(get_translation("unknown_command", language))
                    return
                transaction.amount = amount
                self.db.commit()
                # Clear edit flags
                context.user_data.pop('edit_mode', None)
                context.user_data.pop('editing_transaction_id', None)
                context.user_data.pop('amount_buffer', None)
                context.user_data.pop('waiting_for_amount', None)
                # Confirmation
                confirm_text = get_translation("transaction_updated", language) if get_translation("transaction_updated", language) else "✅ Updated"
                await update.callback_query.edit_message_text(
                    confirm_text,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_translation('back_to_manage', language), callback_data='manage_transactions')]])
                )
            else:
                # Process a new transaction
                await self._process_transaction(update, context, amount, language)
            return
        
        # Handle backspace button
        if callback_data == "amount_backspace":
            if context.user_data['amount_buffer']:
                context.user_data['amount_buffer'] = context.user_data['amount_buffer'][:-1]
            # Show current buffer
            await self._show_amount_buffer_callback(update, context, language)
            return
        
        # Handle digit and dot input
        if callback_data.startswith("amount_"):
            digit = callback_data.replace("amount_", "")
            
            # Handle dot
            if digit == "dot":
                # Prevent multiple dots
                if "." in context.user_data['amount_buffer']:
                    await update.callback_query.answer()
                    return
                digit = "."
            
            # Limit buffer length
            if len(context.user_data['amount_buffer']) >= 10:
                await update.callback_query.answer()
                return
            
            context.user_data['amount_buffer'] += digit
            await self._show_amount_buffer_callback(update, context, language)
            return
    
    async def _show_amount_buffer_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
        """Show current amount buffer to user via callback query"""
        buffer = context.user_data.get('amount_buffer', '')
        if not buffer:
            buffer = "0"
        
        # Get category info for display
        category_id = context.user_data.get('selected_category_id')
        category = self.db.query(Category).filter(Category.id == category_id).first()
        selected_currency = context.user_data.get('selected_currency', 'USD')
        
        if category:
            header_key = 'add_income' if category.category_type == CategoryType.INCOME else 'add_expense'
            currency_info = SUPPORTED_CURRENCIES.get(selected_currency, {})
            currency_symbol = currency_info.get("symbol", selected_currency)
            
            message = f"{get_translation(header_key, language)}\n\n"
            message += f"{get_translation('category', language)}: {category.icon} {category.get_name(language)}\n\n"
            message += f"{get_translation('amount', language)}: **{buffer}**"
        else:
            message = f"{get_translation('amount', language)}: **{buffer}**"
        
        await update.callback_query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=get_amount_keyboard(language)
        )
    
    async def _process_transaction(self, update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float, language: str):
        """Process the transaction with the given amount"""
        category_id = context.user_data.get('selected_category_id')
        category = self.db.query(Category).filter(Category.id == category_id).first()
        
        if not category:
            await update.message.reply_text("Category not found.")
            return
        
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        # Get selected currency and date
        selected_currency = context.user_data.get('selected_currency', user.preferred_currency or 'USD')
        selected_date = context.user_data.get('selected_date', datetime.now().date())
        
        # Create transaction
        transaction = Transaction(
            amount=amount,
            currency=selected_currency,
            user_id=user.id,  # This is now the group's ID if it's a group
            category_id=category.id,
            description="",
            transaction_date=datetime.combine(selected_date, datetime.now().time())
        )
        
        self.db.add(transaction)
        self.db.commit()

        # If expense and primary income category configured, ensure future balances reflect deduction in UI
        # (We keep derived balance via queries; no separate table write needed here.)
        
        # Clear user data
        context.user_data.pop('waiting_for_amount', None)
        context.user_data.pop('waiting_for_custom_date', None)
        context.user_data.pop('selected_category_id', None)
        context.user_data.pop('selected_currency', None)
        context.user_data.pop('selected_date', None)
        context.user_data.pop('amount_buffer', None)
        
        # Get user's preferred language and currency
        currency_symbol = get_currency_symbol(selected_currency)
        
        type_emoji = "💰" if category.category_type == CategoryType.INCOME else "💸"
        transaction_type = get_translation("income", language) if category.category_type == CategoryType.INCOME else get_translation("expense", language)
        
        success_message = get_translation(
            "transaction_added",
            language,
            currency_symbol=currency_symbol,
            amount=amount,
            category_icon=category.icon,
            category_name=category.get_name(language),
            transaction_type=transaction_type
        )
        
        # Add buttons for "Add More" and "Main Menu"
        # "Add more" should reopen the same flow (expense or income)
        add_more_callback = "add_income" if category.category_type == CategoryType.INCOME else "add_expense"
        keyboard = [
            [InlineKeyboardButton(
                get_translation("add_more", language), 
                callback_data=add_more_callback
            )],
            [InlineKeyboardButton(
                get_translation("back_to_main", language), 
                callback_data="main_menu"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            success_message,
            reply_markup=reply_markup
        )
    
    async def handle_recent_transactions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle view recent transactions"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        user_currency = user.preferred_currency if user else "USD"
        
        if not user:
            await update.callback_query.answer("Please use /start first to initialize your account.")
            return
        
        # No need to check for group context - unified logic handles both
        
        # Get recent personal transactions (last 10)
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user.id
        ).order_by(desc(Transaction.transaction_date)).limit(10).all()
        
        if not transactions:
            await update.callback_query.edit_message_text(
                "📋 **Recent Transactions**\n\nNo transactions found. Start by adding some income or expenses!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="add_transaction")]]),
                parse_mode='Markdown'
            )
            return
        
        message = "📋 **Recent Transactions**\n\n"
        for i, transaction in enumerate(transactions, 1):
            type_emoji = "💰" if transaction.is_income else "💸"
            date_str = transaction.transaction_date.strftime("%Y-%m-%d %H:%M")
            message += f"{i:2d}. {type_emoji} {user_currency} {transaction.amount:,.2f} - {transaction.category.icon} {transaction.category.get_name(language)}\n"
            message += f"     📅 {date_str}\n"
            if transaction.description:
                message += f"     📝 {transaction.description}\n"
            message += "\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="add_transaction")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_manage_transactions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle transaction management menu"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        if not user:
            await update.callback_query.answer("Please use /start first to initialize your account.")
            return
        
        message = f"📋 **{get_translation('manage_transactions', language)}**\n\n"
        message += f"{get_translation('select_period_to_manage', language)}:\n\n"
        
        keyboard = [
            [InlineKeyboardButton(
                get_translation("today", language),
                callback_data="manage_transactions_today"
            )],
            [InlineKeyboardButton(
                get_translation("this_week", language),
                callback_data="manage_transactions_week"
            )],
            [InlineKeyboardButton(
                get_translation("this_month", language),
                callback_data="manage_transactions_month"
            )],
            [InlineKeyboardButton(
                get_translation("all_transactions", language),
                callback_data="manage_transactions_all"
            )],
            [InlineKeyboardButton(
                get_translation("back_to_main", language),
                callback_data="main_menu"
            )]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_manage_specific_transaction(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle management of a specific transaction"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        if not user:
            await update.callback_query.answer("Please use /start first to initialize your account.")
            return
        
        # Extract transaction ID from callback data
        transaction_id = int(update.callback_query.data.replace("manage_transaction_", ""))
        transaction = self.db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user.id
        ).first()
        
        if not transaction:
            await update.callback_query.answer("Transaction not found.")
            return
        
        # Display transaction details
        type_emoji = "💰" if transaction.is_income else "💸"
        type_name = get_translation("income", language) if transaction.is_income else get_translation("expense", language)
        currency = get_currency_symbol(transaction.currency)
        date_str = transaction.transaction_date.strftime("%Y-%m-%d %H:%M")
        
        message = f"📋 **{get_translation('transaction_details', language)}**\n\n"
        message += f"**{type_name}:** {type_emoji} {currency}{transaction.amount:,.2f}\n"
        message += f"**{get_translation('category', language)}:** {transaction.category.icon} {transaction.category.get_name(language)}\n"
        message += f"**{get_translation('date', language)}:** {date_str}\n"
        if transaction.description:
            message += f"**{get_translation('description', language)}:** {transaction.description}\n"
        
        keyboard = [
            [InlineKeyboardButton(
                get_translation("edit_transaction", language),
                callback_data=f"edit_transaction_{transaction.id}"
            )],
            [InlineKeyboardButton(
                get_translation("delete_transaction", language),
                callback_data=f"delete_transaction_{transaction.id}"
            )],
            [InlineKeyboardButton(
                get_translation("back_to_main", language),
                callback_data="main_menu"
            )]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_edit_transaction(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle editing a transaction"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        if not user:
            await update.callback_query.answer("Please use /start first to initialize your account.")
            return
        
        # Extract transaction ID and optional sub-action
        data = update.callback_query.data
        action = None
        transaction_id = None
        try:
            if data.startswith("edit_transaction_amount_"):
                action = "amount"
                transaction_id = int(data.split("_")[-1])
            elif data.startswith("edit_transaction_category_"):
                action = "category"
                transaction_id = int(data.split("_")[-1])
            elif data.startswith("edit_transaction_date_"):
                action = "date"
                transaction_id = int(data.split("_")[-1])
            elif data.startswith("edit_transaction_description_"):
                action = "description"
                transaction_id = int(data.split("_")[-1])
            else:
                # plain edit_transaction_{id}
                transaction_id = int(data.replace("edit_transaction_", ""))
        except ValueError:
            await update.callback_query.answer(get_translation("unknown_command", language))
            return

        transaction = self.db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user.id
        ).first()
        
        if not transaction:
            await update.callback_query.answer("Transaction not found.")
            return
        
        # If a specific field was requested, branch early
        if action == "amount":
            # Prepare inline amount edit flow
            context.user_data['editing_transaction_id'] = transaction_id
            context.user_data['edit_mode'] = 'amount'
            context.user_data['waiting_for_amount'] = True
            context.user_data['amount_buffer'] = ""
            # For header rendering
            context.user_data['selected_category_id'] = transaction.category_id
            context.user_data['selected_currency'] = transaction.currency

            currency_symbol = get_currency_symbol(transaction.currency)
            await update.callback_query.edit_message_text(
                f"✏️ {get_translation('amount', language)}\n\n"
                f"{currency_symbol} {float(transaction.amount):,.2f}\n\n"
                f"{get_translation('enter_amount', language)}",
                parse_mode='Markdown',
                reply_markup=get_amount_keyboard(language)
            )
            return

        # Store transaction ID for editing (generic menu)
        context.user_data['editing_transaction_id'] = transaction_id
        
        message = f"✏️ **{get_translation('edit_transaction', language)}**\n\n"
        message += f"{get_translation('what_to_edit', language)}:\n\n"
        
        keyboard = [
            [InlineKeyboardButton(
                f"💰 {get_translation('amount', language)}",
                callback_data=f"edit_transaction_amount_{transaction.id}"
            )],
            [InlineKeyboardButton(
                f"🏷️ {get_translation('category', language)}",
                callback_data=f"edit_transaction_category_{transaction.id}"
            )],
            [InlineKeyboardButton(
                f"📅 {get_translation('date', language)}",
                callback_data=f"edit_transaction_date_{transaction.id}"
            )],
            [InlineKeyboardButton(
                f"📝 {get_translation('description', language)}",
                callback_data=f"edit_transaction_description_{transaction.id}"
            )],
            [InlineKeyboardButton(
                get_translation("back_to_main", language),
                callback_data="main_menu"
            )]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_delete_transaction(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle deleting a transaction"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        if not user:
            await update.callback_query.answer("Please use /start first to initialize your account.")
            return
        
        # Extract transaction ID from callback data
        transaction_id = int(update.callback_query.data.replace("delete_transaction_", ""))
        transaction = self.db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user.id
        ).first()
        
        if not transaction:
            await update.callback_query.answer("Transaction not found.")
            return
        
        # Delete the transaction
        self.db.delete(transaction)
        self.db.commit()
        
        await update.callback_query.edit_message_text(
            get_translation("transaction_deleted", language)
        )
    
    async def handle_manage_transactions_period(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle transaction management for specific period"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        if not user:
            await update.callback_query.answer("Please use /start first to initialize your account.")
            return
        
        # Extract period from callback data
        callback_data = update.callback_query.data
        
        # Remove "manage_transactions_" prefix
        period_with_page = callback_data.replace("manage_transactions_", "")
        
        # Extract period (everything before "_page_")
        if "_page_" in period_with_page:
            period = period_with_page.split("_page_")[0]
        else:
            period = period_with_page
        
        # Calculate date range based on period
        today = datetime.now().date()
        
        if period == "today":
            start_date = today
            end_date = today
            period_name = get_translation("today", language)
        elif period == "week":
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
            period_name = get_translation("this_week", language)
        elif period == "month":
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            period_name = get_translation("this_month", language)
        else:  # all
            start_date = None
            end_date = None
            period_name = get_translation("all_transactions", language)
        
        # Get transactions for the period
        query = self.db.query(Transaction).filter(Transaction.user_id == user.id)
        
        if start_date and end_date:
            query = query.filter(
                func.date(Transaction.transaction_date) >= start_date,
                func.date(Transaction.transaction_date) <= end_date
            )
        
        # Get total count for pagination
        total_count = query.count()
        
        if total_count == 0:
            message = f"📋 **{get_translation('manage_transactions', language)}**\n\n"
            message += f"📅 **{period_name}**\n\n"
            message += f"❌ {get_translation('no_transactions_in_period', language)}"
            
            keyboard = [
                [InlineKeyboardButton(
                    get_translation("back_to_manage", language),
                    callback_data="manage_transactions"
                )]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        # Get page from callback data or default to 0
        page = 0
        if "_page_" in callback_data:
            try:
                page_str = callback_data.split("_page_")[-1]
                page = int(page_str)
            except (ValueError, IndexError):
                page = 0
        
        # Calculate pagination
        per_page = 5
        offset = page * per_page
        total_pages = (total_count + per_page - 1) // per_page
        
        # Get transactions for current page
        transactions = query.order_by(desc(Transaction.transaction_date)).offset(offset).limit(per_page).all()
        
        # Build message with period info
        message = f"📋 **{get_translation('manage_transactions', language)}**\n\n"
        message += f"📅 **{period_name}**\n"
        if start_date and end_date:
            if start_date == end_date:
                message += f"📆 {start_date.strftime('%Y-%m-%d')}\n\n"
            else:
                message += f"📆 {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}\n\n"
        else:
            message += f"📆 {get_translation('all_time', language)}\n\n"
        
        message += f"{get_translation('select_transaction_to_manage', language)}:\n"
        # Show page info only if there is more than one page
        if total_pages > 1:
            message += f"📄 {get_translation('page', language)} {page + 1}/{total_pages} ({total_count} {get_translation('transactions', language)})\n\n"
        else:
            message += "\n"
        
        # Build keyboard with transactions
        keyboard = []
        for i, transaction in enumerate(transactions):
            # Calculate global transaction number (continues across pages)
            global_number = offset + i + 1
            date_str = transaction.transaction_date.strftime("%d.%m %H:%M")
            amount = transaction.amount
            currency = get_currency_symbol(transaction.currency)
            category_name = transaction.category.get_name(language)
            
            # Format with date, left alignment, and space after currency (no icons)
            button_text = f"{global_number:2d}. {date_str} - {currency} {amount} - {category_name}"
            if len(button_text) > 50:  # Telegram button text limit
                button_text = f"{global_number:2d}. {date_str} - {currency} {amount}"
            
            keyboard.append([InlineKeyboardButton(
                button_text,
                callback_data=f"manage_transaction_{transaction.id}"
            )])
        
        # Add pagination buttons only if more than one page
        pagination_buttons = []
        
        # Previous button (only if not on first page)
        if total_pages > 1 and page > 0:
            pagination_buttons.append(InlineKeyboardButton(
                "⬅️",
                callback_data=f"manage_transactions_{period}_page_{page - 1}"
            ))
        
        # Page number buttons
        start_page = max(0, page - 2)
        end_page = min(total_pages - 1, page + 2)
        
        if total_pages > 1:
            for p in range(start_page, end_page + 1):
                if p == page:
                    # Current page - show as selected
                    pagination_buttons.append(InlineKeyboardButton(
                        f"•{p + 1}•",
                        callback_data=f"manage_transactions_{period}_page_{p}"
                    ))
                else:
                    # Other pages
                    pagination_buttons.append(InlineKeyboardButton(
                        str(p + 1),
                        callback_data=f"manage_transactions_{period}_page_{p}"
                    ))
        
        # Next button (only if not on last page)
        if total_pages > 1 and page < total_pages - 1:
            pagination_buttons.append(InlineKeyboardButton(
                "➡️",
                callback_data=f"manage_transactions_{period}_page_{page + 1}"
            ))
        
        if total_pages > 1 and pagination_buttons:
            keyboard.append(pagination_buttons)
        
        # Add back button + Recent transactions
        keyboard.append([
            InlineKeyboardButton(
                get_translation("back_to_manage", language),
                callback_data="manage_transactions"
            ),
            InlineKeyboardButton(
                get_translation('recent_transactions', language),
                callback_data='recent_transactions'
            )
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
