from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract
from datetime import datetime, timedelta
from src.models.user import User
from src.models.category import Category, CategoryType
from src.models.transaction import Transaction
from src.utils.translations import get_translation
from .base import BaseHandler

class ReportHandler(BaseHandler):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Default handle method - not used in this handler"""
        pass
    
    async def handle_view_reports(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle view reports menu"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        
        language = user.preferred_language if user else "en"
        
        keyboard = [
            [InlineKeyboardButton(
                get_translation('balance', language), 
                callback_data="balance_report"
            )],
            [InlineKeyboardButton(
                get_translation('analytics', language), 
                callback_data="analytics"
            )],
            [InlineKeyboardButton(
                get_translation('weekly_report', language), 
                callback_data="weekly_report"
            )],
            [InlineKeyboardButton(
                get_translation('monthly_report', language), 
                callback_data="monthly_report"
            )],
            [InlineKeyboardButton(
                get_translation('yearly_report', language), 
                callback_data="yearly_report"
            )],
            [InlineKeyboardButton(
                get_translation('category_breakdown', language), 
                callback_data="category_breakdown"
            )],
            [InlineKeyboardButton(
                get_translation('custom_period', language), 
                callback_data="custom_period"
            )],
            [InlineKeyboardButton(
                get_translation('back_to_main', language), 
                callback_data="main_menu"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            get_translation("reports_menu", language),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_balance_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show balance by categories (totals per category)"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        user_currency = user.preferred_currency if user else "USD"
        
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        
        # All-time totals
        total_income = self.db.query(func.coalesce(func.sum(Transaction.amount), 0)).join(Category).filter(
            Transaction.user_id == user.id,
            Transaction.currency == user_currency,
            Category.category_type == CategoryType.INCOME
        ).scalar() or 0
        total_expense = self.db.query(func.coalesce(func.sum(Transaction.amount), 0)).join(Category).filter(
            Transaction.user_id == user.id,
            Transaction.currency == user_currency,
            Category.category_type == CategoryType.EXPENSE
        ).scalar() or 0
        remaining = float(total_income) - float(total_expense)

        # Income totals by category (all time)
        rows = self.db.query(
            Category.id,
            Category.name_en,
            Category.name_ru,
            Category.icon,
            func.coalesce(func.sum(Transaction.amount), 0).label('total')
        ).join(Transaction, Transaction.category_id == Category.id).filter(
            Transaction.user_id == user.id,
            Transaction.currency == user_currency,
            Category.category_type == CategoryType.INCOME
        ).group_by(Category.id, Category.name_en, Category.name_ru, Category.icon).order_by(desc('total')).all()

        income_lines = []
        for cid, name_en, name_ru, icon, total in rows:
            localized_name = name_ru if language == "ru" else name_en
            line = f"{icon} {localized_name}: {user_currency} {float(total):,.0f}"
            income_lines.append(line)

        # Build message: show remaining balance and income by category; no expense section
        title = get_translation('balance', language)
        remaining_label = 'Remaining' if language != 'ru' else 'Остаток'
        income_label = get_translation('income', language)
        
        # Avoid duplicate emoji: translation already contains the icon
        message = f"**{title}**\n\n{remaining_label}: {user_currency} {remaining:,.0f}\n\n"
        if income_lines:
            message += f"{income_label}:\n" + "\n".join(income_lines)
        else:
            message += get_translation('no_transactions', language)
        
        keyboard = [[InlineKeyboardButton(get_translation('back_to_reports', language), callback_data='view_reports')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_monthly_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle monthly report"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        user_currency = user.preferred_currency if user else "USD"
        
        # Get current month transactions
        now = datetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get income for current month
        income = self.db.query(func.sum(Transaction.amount)).join(Category).filter(
            Transaction.user_id == user.id,
            Category.category_type == CategoryType.INCOME,
            Transaction.transaction_date >= start_of_month
        ).scalar() or 0
        
        # Get expenses for current month
        expenses = self.db.query(func.sum(Transaction.amount)).join(Category).filter(
            Transaction.user_id == user.id,
            Category.category_type == CategoryType.EXPENSE,
            Transaction.transaction_date >= start_of_month
        ).scalar() or 0
        
        # Get top expense categories
        top_expense_categories = self.db.query(
            Category.name_en,
            Category.name_ru,
            Category.icon,
            func.sum(Transaction.amount).label('total')
        ).join(Transaction).filter(
            Transaction.user_id == user.id,
            Category.category_type == CategoryType.EXPENSE,
            Transaction.transaction_date >= start_of_month
        ).group_by(Category.id, Category.name_en, Category.name_ru, Category.icon).order_by(desc('total')).limit(5).all()
        
        balance = float(income) - float(expenses)
        month_name = now.strftime("%Y-%m")
        
        message = f"**{get_translation('monthly_report', language)} - {month_name}**\n\n"
        message += f"**{get_translation('total_income', language)}**: {user_currency} {income:,.2f}\n"
        message += f"**{get_translation('total_expense', language)}**: {user_currency} {expenses:,.2f}\n"
        message += f"**{get_translation('net_amount', language)}**: {user_currency} {balance:,.2f}\n\n"
        
        if top_expense_categories:
            message += f"🏆 **{get_translation('top_expense_categories', language)}:**\n"
            for cat_name_en, cat_name_ru, icon, total in top_expense_categories:
                percentage = (float(total) / float(expenses) * 100) if expenses > 0 else 0
                localized_name = cat_name_ru if language == "ru" else cat_name_en
                message += f"• {icon} {localized_name}: {user_currency} {total:,.2f} ({percentage:.1f}%)\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="view_reports")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_yearly_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle yearly report"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        user_currency = user.preferred_currency if user else "USD"
        
        # Get current year transactions
        now = datetime.now()
        start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get income for current year
        income = self.db.query(func.sum(Transaction.amount)).join(Category).filter(
            Transaction.user_id == user.id,
            Category.category_type == CategoryType.INCOME,
            Transaction.transaction_date >= start_of_year
        ).scalar() or 0
        
        # Get expenses for current year
        expenses = self.db.query(func.sum(Transaction.amount)).join(Category).filter(
            Transaction.user_id == user.id,
            Category.category_type == CategoryType.EXPENSE,
            Transaction.transaction_date >= start_of_year
        ).scalar() or 0
        
        # Get monthly breakdown
        monthly_data = self.db.query(
            extract('month', Transaction.transaction_date).label('month'),
            func.sum(Transaction.amount).label('total')
        ).join(Category).filter(
            Transaction.user_id == user.id,
            Category.category_type == CategoryType.EXPENSE,
            Transaction.transaction_date >= start_of_year
        ).group_by(extract('month', Transaction.transaction_date)).all()
        
        balance = float(income) - float(expenses)
        year = now.year
        
        message = f"**{get_translation('yearly_report', language)} - {year}**\n\n"
        message += f"**{get_translation('total_income', language)}**: {user_currency} {income:,.2f}\n"
        message += f"**{get_translation('total_expense', language)}**: {user_currency} {expenses:,.2f}\n"
        message += f"**{get_translation('net_amount', language)}**: {user_currency} {balance:,.2f}\n\n"
        
        if monthly_data:
            message += f"📅 **{get_translation('monthly_expense_breakdown', language)}:**\n"
            for month_num, total in monthly_data:
                message += f"• {int(month_num):02d}: {user_currency} {total:,.2f}\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="view_reports")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_category_breakdown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle category breakdown report"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        user_currency = user.preferred_currency if user else "USD"
        
        # Get all categories with their totals
        category_totals = self.db.query(
            Category.name_en,
            Category.name_ru,
            Category.category_type,
            Category.icon,
            func.sum(Transaction.amount).label('total'),
            func.count(Transaction.id).label('count')
        ).join(Transaction).filter(
            Transaction.user_id == user.id
        ).group_by(Category.id, Category.name_en, Category.name_ru, Category.category_type, Category.icon).all()
        
        if not category_totals:
            await update.callback_query.edit_message_text(
                f"{get_translation('category_breakdown', language)}\n\n{get_translation('no_transactions', language)}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_translation('back_to_reports', language), callback_data="view_reports")]]),
                parse_mode='Markdown'
            )
            return
        
        # Separate income and expense categories
        income_categories = [cat for cat in category_totals if cat.category_type == CategoryType.INCOME]
        expense_categories = [cat for cat in category_totals if cat.category_type == CategoryType.EXPENSE]
        
        message = f"**{get_translation('category_breakdown', language)}**\n\n"
        
        if income_categories:
            message += f"💰 **{get_translation('income_categories', language)}:**\n"
            for cat_name_en, cat_name_ru, cat_type, icon, total, count in income_categories:
                localized_name = cat_name_ru if language == "ru" else cat_name_en
                message += f"• {icon} {localized_name}: {user_currency} {total:,.2f} ({count} {get_translation('transactions', language)})\n"
            message += "\n"
        
        if expense_categories:
            message += f"💸 **{get_translation('expense_categories', language)}:**\n"
            for cat_name_en, cat_name_ru, cat_type, icon, total, count in expense_categories:
                localized_name = cat_name_ru if language == "ru" else cat_name_en
                message += f"• {icon} {localized_name}: {user_currency} {total:,.2f} ({count} {get_translation('transactions', language)})\n"
        
        keyboard = [[InlineKeyboardButton(get_translation('back_to_reports', language), callback_data="view_reports")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_custom_period_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle custom period report"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        if not user:
            await update.callback_query.answer("Please use /start first to initialize your account.")
            return
        
        # Set state for custom period input
        context.user_data['waiting_for_custom_period'] = True
        
        message = get_translation("custom_period_instructions", language)
        keyboard = [[InlineKeyboardButton(
            get_translation("back_to_main", language), 
            callback_data="view_reports"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_custom_period_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle custom period input (format: YYYY-MM-DD to YYYY-MM-DD)"""
        if not context.user_data.get('waiting_for_custom_period'):
            return
        
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        try:
            # Parse input format: "2024-01-01 to 2024-01-31"
            input_text = update.message.text.strip()
            if " to " not in input_text:
                raise ValueError("Invalid format")
            
            start_str, end_str = input_text.split(" to ")
            start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d")
            end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d")
            
            if start_date > end_date:
                raise ValueError("Start date must be before end date")
            
            # Get transactions in the period
            transactions = self.db.query(Transaction).join(Category).filter(
                Transaction.user_id == user.id,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            ).order_by(desc(Transaction.transaction_date)).all()
            
            if not transactions:
                message = get_translation("no_transactions_period", language).format(
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d")
                )
            else:
                # Calculate totals
                income = sum(t.amount for t in transactions if t.category.category_type == CategoryType.INCOME)
                expenses = sum(t.amount for t in transactions if t.category.category_type == CategoryType.EXPENSE)
                balance = income - expenses
                
                message = get_translation("custom_period_report", language).format(
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d"),
                    total_transactions=len(transactions),
                    income=income,
                    expenses=expenses,
                    balance=balance
                )
                
                # Add recent transactions
                message += f"\n\n**{get_translation('recent_transactions', language)}:**\n"
                for transaction in transactions[:10]:  # Show last 10
                    type_emoji = "💰" if transaction.category.category_type == CategoryType.INCOME else "💸"
                    message += f"{type_emoji} {user_currency} {transaction.amount:,.2f} - {transaction.category.icon} {transaction.category.get_name(language)}\n"
            
            keyboard = [[InlineKeyboardButton(
                get_translation("back_to_main", language), 
                callback_data="view_reports"
            )]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except ValueError as e:
            error_message = get_translation("invalid_date_format", language)
            await update.message.reply_text(error_message)
            return
        
        # Clear the waiting state
        context.user_data.pop('waiting_for_custom_period', None)
    
    async def handle_analytics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle analytics menu"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        if not user:
            await update.callback_query.answer("Please use /start first to initialize your account.")
            return
        
        # Calculate some basic analytics
        total_transactions = self.db.query(func.count(Transaction.id)).filter(
            Transaction.user_id == user.id
        ).scalar() or 0
        
        # Average transaction amount
        avg_amount = self.db.query(func.avg(Transaction.amount)).filter(
            Transaction.user_id == user.id
        ).scalar() or 0
        
        # Most used category
        most_used_category = self.db.query(
            Category.name_en,
            Category.name_ru,
            Category.icon,
            func.count(Transaction.id).label('count')
        ).join(Transaction).filter(
            Transaction.user_id == user.id
        ).group_by(Category.id, Category.name_en, Category.name_ru, Category.icon).order_by(desc('count')).first()
        
        # Days since first transaction
        first_transaction = self.db.query(Transaction.transaction_date).filter(
            Transaction.user_id == user.id
        ).order_by(Transaction.transaction_date).first()
        
        days_active = 0
        if first_transaction:
            from datetime import timezone
            now = datetime.now(timezone.utc)
            days_active = (now - first_transaction.transaction_date).days
        
        language = user.preferred_language if user else "en"
        user_currency = user.preferred_currency if user else "USD"
        
        message = f"📈 **{get_translation('analytics_dashboard', language)}**\n\n"
        message += f"📊 **{get_translation('total_transactions', language)}**: {total_transactions}\n"
        message += f"💰 **{get_translation('average_amount', language)}**: {user_currency} {avg_amount:,.2f}\n"
        message += f"📅 **{get_translation('days_active', language)}**: {days_active} {get_translation('days', language)}\n\n"
        
        if most_used_category:
            localized_name = most_used_category.name_ru if language == "ru" else most_used_category.name_en
            message += f"🏆 **{get_translation('most_used_category', language)}**: {most_used_category.icon} {localized_name} ({most_used_category.count} {get_translation('times', language)})\n\n"
        
        message += f"💡 **{get_translation('tips', language)}:**\n"
        message += f"• {get_translation('tip_track_daily', language)}\n"
        message += f"• {get_translation('tip_review_monthly', language)}\n"
        message += f"• {get_translation('tip_use_categories', language)}\n"
        
        keyboard = [
            [InlineKeyboardButton(
                get_translation('view_reports', language), 
                callback_data="view_reports"
            )],
            [InlineKeyboardButton(
                get_translation('back_to_main', language), 
                callback_data="main_menu"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_weekly_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle weekly report"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        user_currency = user.preferred_currency if user else "USD"
        
        if not user:
            await update.callback_query.answer("Please use /start first to initialize your account.")
            return
        
        # Calculate current week (Monday to Sunday)
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # Get transactions for current week
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user.id,
            func.date(Transaction.transaction_date) >= start_of_week,
            func.date(Transaction.transaction_date) <= end_of_week
        ).all()
        
        if not transactions:
            message = f"📅 **{get_translation('weekly_report', language)}**\n\n"
            message += f"📊 **{get_translation('period', language)}**: {start_of_week.strftime('%Y-%m-%d')} - {end_of_week.strftime('%Y-%m-%d')}\n\n"
            message += f"❌ {get_translation('no_transactions_this_week', language)}"
            
            keyboard = [
                [InlineKeyboardButton(
                    get_translation('back_to_reports', language), 
                    callback_data="view_reports"
                )]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        # Calculate totals
        total_income = sum(t.amount for t in transactions if t.is_income)
        total_expense = sum(t.amount for t in transactions if t.is_expense)
        net_amount = total_income - total_expense
        
        # Group by category
        category_totals = {}
        for transaction in transactions:
            category_name = transaction.category.get_name(language)
            if category_name not in category_totals:
                category_totals[category_name] = {'income': 0, 'expense': 0, 'icon': transaction.category.icon}
            
            if transaction.is_income:
                category_totals[category_name]['income'] += transaction.amount
            else:
                category_totals[category_name]['expense'] += transaction.amount
        
        # Build message (avoid duplicate emojis: icons live in translations and category.icon)
        message = f"**{get_translation('weekly_report', language)}**\n\n"
        message += f"**{get_translation('period', language)}**: {start_of_week.strftime('%Y-%m-%d')} - {end_of_week.strftime('%Y-%m-%d')}\n\n"

        message += f"**{get_translation('total_income', language)}**: {user_currency} {total_income:,.2f}\n"
        message += f"**{get_translation('total_expense', language)}**: {user_currency} {total_expense:,.2f}\n"
        message += f"**{get_translation('net_amount', language)}**: {user_currency} {net_amount:,.2f}\n\n"

        if category_totals:
            message += f"**{get_translation('by_category', language)}**:\n"
            for category_name, totals in sorted(category_totals.items(), key=lambda x: x[1]['expense'] + x[1]['income'], reverse=True):
                if totals['income'] > 0:
                    message += f"{totals['icon']} {category_name}: {user_currency} {totals['income']:,.2f}\n"
                if totals['expense'] > 0:
                    message += f"{totals['icon']} {category_name}: {user_currency} {totals['expense']:,.2f}\n"
        
        keyboard = [
            [InlineKeyboardButton(
                get_translation('back_to_reports', language), 
                callback_data="view_reports"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
