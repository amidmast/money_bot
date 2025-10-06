from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from src.models.user import User
from src.models.category import Category, CategoryType
from src.models.transaction import Transaction
from src.utils.translations import get_translation
from .base import BaseHandler

class CategoryHandler(BaseHandler):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Default handle method - not used in this handler"""
        pass
    
    async def handle_manage_categories(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle category management menu"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        
        language = user.preferred_language if user else "en"
        
        keyboard = [
            [InlineKeyboardButton(
                get_translation('add_new_category', language), 
                callback_data="add_category"
            )],
            [InlineKeyboardButton(
                get_translation('view_all_categories', language), 
                callback_data="view_categories"
            )],
            [InlineKeyboardButton(
                get_translation('edit_category', language), 
                callback_data="edit_category"
            )],
            [InlineKeyboardButton(
                get_translation('delete_category', language), 
                callback_data="delete_category"
            )],
            [InlineKeyboardButton(
                get_translation('back_to_main', language), 
                callback_data="main_menu"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        menu_text = get_translation("manage_categories_menu", language)
        if not menu_text.strip():
            menu_text = "🏷️ Category Management"
        
        await update.callback_query.edit_message_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_add_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle add category callback"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        keyboard = [
            [InlineKeyboardButton(
                get_translation('add_income_category', language), 
                callback_data="add_income_category"
            )],
            [InlineKeyboardButton(
                get_translation('add_expense_category', language), 
                callback_data="add_expense_category"
            )],
            [InlineKeyboardButton(
                get_translation('back_to_main', language), 
                callback_data="manage_categories"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            get_translation("add_category_menu", language),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_add_income_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle add income category"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        context.user_data['category_type'] = CategoryType.INCOME
        context.user_data['category_step'] = 'name_en'
        
        await update.callback_query.edit_message_text(
            get_translation("enter_category_name_en", language),
            parse_mode='Markdown'
        )
        context.user_data['waiting_for_category_name'] = True
    
    async def handle_add_expense_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle add expense category"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        context.user_data['category_type'] = CategoryType.EXPENSE
        context.user_data['category_step'] = 'name_en'
        
        await update.callback_query.edit_message_text(
            get_translation("enter_category_name_en", language),
            parse_mode='Markdown'
        )
        context.user_data['waiting_for_category_name'] = True
    
    async def handle_category_name_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle category name input"""
        if not context.user_data.get('waiting_for_category_name'):
            return
        
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        category_name = update.message.text.strip()
        category_type = context.user_data.get('category_type')
        current_step = context.user_data.get('category_step', 'name_en')
        
        if not category_name:
            await update.message.reply_text(get_translation("invalid_category_name", language))
            return
        
        # Store the current name
        if current_step == 'name_en':
            context.user_data['category_name_en'] = category_name
            context.user_data['category_step'] = 'name_ru'
            await update.message.reply_text(
                get_translation("enter_category_name_ru", language),
                parse_mode='Markdown'
            )
        elif current_step == 'name_ru':
            context.user_data['category_name_ru'] = category_name
            # Now create the category
            await self._create_category(update, context, user, language)
    
    async def _create_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, language: str):
        """Create a new category with multilingual names"""
        category_name_en = context.user_data.get('category_name_en')
        category_name_ru = context.user_data.get('category_name_ru')
        category_type = context.user_data.get('category_type')
        
        # Check if category already exists (check both languages)
        existing_category = self.db.query(Category).filter(
            Category.user_id == user.id,
            Category.category_type == category_type,
            (Category.name_en == category_name_en) | (Category.name_ru == category_name_ru)
        ).first()
        
        if existing_category:
            await update.message.reply_text(
                get_translation("category_already_exists", language)
            )
            return
        
        # Create new category with multilingual names
        new_category = Category(
            name_en=category_name_en,
            name_ru=category_name_ru,
            category_type=category_type,
            user_id=user.id,
            color="#3498db",  # Default color
            icon="📝"  # Default icon
        )
        
        self.db.add(new_category)
        self.db.commit()
        
        # Clear user data
        context.user_data.pop('waiting_for_category_name', None)
        context.user_data.pop('category_type', None)
        context.user_data.pop('category_step', None)
        context.user_data.pop('category_name_en', None)
        context.user_data.pop('category_name_ru', None)
        
        type_emoji = "💰" if category_type == CategoryType.INCOME else "💸"
        success_message = get_translation("category_created_success", language).format(
            name_en=category_name_en,
            name_ru=category_name_ru
        )
        await update.message.reply_text(
            f"{type_emoji} {success_message}\n\n{get_translation('use_start_to_return', language)}"
        )
    
    async def handle_view_categories(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle view categories"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        
        # Get all categories
        income_categories = self.db.query(Category).filter(
            Category.user_id == user.id,
            Category.category_type == CategoryType.INCOME,
            Category.is_active == True
        ).all()
        
        expense_categories = self.db.query(Category).filter(
            Category.user_id == user.id,
            Category.category_type == CategoryType.EXPENSE,
            Category.is_active == True
        ).all()
        
        message = f"🏷️ **{get_translation('your_categories', language)}**\n\n"
        
        if income_categories:
            message += f"💰 **{get_translation('income_categories', language)}:**\n"
            for cat in income_categories:
                localized_name = cat.get_name(language)
                localized_desc = cat.get_description(language)
                message += f"• {cat.icon} {localized_name}"
                if localized_desc:
                    message += f" - {localized_desc}"
                message += "\n"
            message += "\n"
        
        if expense_categories:
            message += f"💸 **{get_translation('expense_categories', language)}:**\n"
            for cat in expense_categories:
                localized_name = cat.get_name(language)
                localized_desc = cat.get_description(language)
                message += f"• {cat.icon} {localized_name}"
                if localized_desc:
                    message += f" - {localized_desc}"
                message += "\n"
        
        if not income_categories and not expense_categories:
            message += get_translation("no_categories_found", language)
        
        keyboard = [[InlineKeyboardButton(
            get_translation('back_to_main', language), 
            callback_data="manage_categories"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_edit_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle edit category menu"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        
        language = user.preferred_language if user else "en"
        
        # Get user's categories
        categories = self.db.query(Category).filter(
            Category.user_id == user.id,
            Category.is_active == True
        ).all()
        
        if not categories:
            await update.callback_query.edit_message_text(
                get_translation("no_categories_found", language),
                parse_mode='Markdown'
            )
            return
        
        # Create keyboard with categories
        keyboard = []
        for category in categories:
            localized_name = category.get_name(language)
            keyboard.append([InlineKeyboardButton(
                f"{category.icon} {localized_name}",
                callback_data=f"edit_category_{category.id}"
            )])
        
        # Add back button
        keyboard.append([InlineKeyboardButton(
            get_translation('back_to_main', language), 
            callback_data="manage_categories"
        )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            get_translation("select_category_to_edit", language),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_delete_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle delete category menu"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        
        language = user.preferred_language if user else "en"
        
        # Get user's categories
        categories = self.db.query(Category).filter(
            Category.user_id == user.id,
            Category.is_active == True
        ).all()
        
        if not categories:
            await update.callback_query.edit_message_text(
                get_translation("no_categories_found", language),
                parse_mode='Markdown'
            )
            return
        
        # Create keyboard with categories
        keyboard = []
        for category in categories:
            localized_name = category.get_name(language)
            keyboard.append([InlineKeyboardButton(
                f"{category.icon} {localized_name}",
                callback_data=f"delete_category_{category.id}"
            )])
        
        # Add back button
        keyboard.append([InlineKeyboardButton(
            get_translation('back_to_main', language), 
            callback_data="manage_categories"
        )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            get_translation("select_category_to_delete", language),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_edit_specific_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle editing a specific category"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        
        language = user.preferred_language if user else "en"
        
        # Extract category ID from callback data
        callback_data = update.callback_query.data
        category_id = int(callback_data.split("_")[-1])
        
        # Get the category
        category = self.db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == user.id
        ).first()
        
        if not category:
            await update.callback_query.answer(get_translation("category_not_found", language))
            return
        
        # Show edit options menu
        localized_name = category.get_name(language)
        
        keyboard = [
            [InlineKeyboardButton(
                get_translation('edit_name_en', language), 
                callback_data=f"edit_name_en_{category_id}"
            )],
            [InlineKeyboardButton(
                get_translation('edit_name_ru', language), 
                callback_data=f"edit_name_ru_{category_id}"
            )],
            [InlineKeyboardButton(
                get_translation('edit_icon', language), 
                callback_data=f"edit_icon_{category_id}"
            )],
            [InlineKeyboardButton(
                get_translation('edit_color', language), 
                callback_data=f"edit_color_{category_id}"
            )],
            [InlineKeyboardButton(
                get_translation('back_to_main', language), 
                callback_data="manage_categories"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            get_translation("edit_category_name", language).format(
                category_name=localized_name
            ),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_delete_specific_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle deleting a specific category"""
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        
        if not user:
            await update.callback_query.answer(get_translation("user_not_found", "en"))
            return
        
        language = user.preferred_language if user else "en"
        
        # Extract category ID from callback data
        callback_data = update.callback_query.data
        category_id = int(callback_data.split("_")[-1])
        
        # Get the category
        category = self.db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == user.id
        ).first()
        
        if not category:
            await update.callback_query.answer(get_translation("category_not_found", language))
            return
        
        # Check if category has transactions
        transaction_count = self.db.query(Transaction).filter(
            Transaction.category_id == category_id
        ).count()
        
        if transaction_count > 0:
            await update.callback_query.edit_message_text(
                get_translation("cannot_delete_category_with_transactions", language).format(
                    category_name=category.get_name(language),
                    transaction_count=transaction_count
                ),
                parse_mode='Markdown'
            )
            return
        
        # Delete the category
        self.db.delete(category)
        self.db.commit()
        
        await update.callback_query.edit_message_text(
            get_translation("category_deleted", language).format(
                category_name=category.get_name(language)
            ),
            parse_mode='Markdown'
        )
    
    async def handle_edit_name_en(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle editing English name of category"""
        callback_data = update.callback_query.data
        category_id = int(callback_data.split("_")[-1])
        
        context.user_data['waiting_for_category_edit'] = True
        context.user_data['edit_category_id'] = category_id
        context.user_data['edit_field'] = 'name_en'
        
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        await update.callback_query.edit_message_text(
            get_translation("enter_new_name_en", language),
            parse_mode='Markdown'
        )
    
    async def handle_edit_name_ru(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle editing Russian name of category"""
        callback_data = update.callback_query.data
        category_id = int(callback_data.split("_")[-1])
        
        context.user_data['waiting_for_category_edit'] = True
        context.user_data['edit_category_id'] = category_id
        context.user_data['edit_field'] = 'name_ru'
        
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        await update.callback_query.edit_message_text(
            get_translation("enter_new_name_ru", language),
            parse_mode='Markdown'
        )
    
    async def handle_edit_icon(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle editing icon of category"""
        callback_data = update.callback_query.data
        category_id = int(callback_data.split("_")[-1])
        
        context.user_data['waiting_for_category_edit'] = True
        context.user_data['edit_category_id'] = category_id
        context.user_data['edit_field'] = 'icon'
        
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        await update.callback_query.edit_message_text(
            get_translation("enter_new_icon", language),
            parse_mode='Markdown'
        )
    
    async def handle_edit_color(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle editing color of category"""
        callback_data = update.callback_query.data
        category_id = int(callback_data.split("_")[-1])
        
        context.user_data['waiting_for_category_edit'] = True
        context.user_data['edit_category_id'] = category_id
        context.user_data['edit_field'] = 'color'
        
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        await update.callback_query.edit_message_text(
            get_translation("enter_new_color", language),
            parse_mode='Markdown'
        )
    
    async def handle_category_edit_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle category edit input"""
        if not context.user_data.get('waiting_for_category_edit'):
            return
        
        category_id = context.user_data.get('edit_category_id')
        edit_field = context.user_data.get('edit_field')
        new_value = update.message.text.strip()
        
        user_data = self.get_context_from_update(update)
        user = self.db.query(User).filter(User.telegram_id == user_data['telegram_id']).first()
        language = user.preferred_language if user else "en"
        
        # Get the category
        category = self.db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == user.id
        ).first()
        
        if not category:
            await update.message.reply_text(get_translation("category_not_found", language))
            return
        
        # Validate and update the field
        if edit_field == 'color':
            # Validate hex color
            if not new_value.startswith('#') or len(new_value) != 7:
                await update.message.reply_text(get_translation("invalid_color", language))
                return
        
        # Update the category
        if edit_field == 'name_en':
            category.name_en = new_value
        elif edit_field == 'name_ru':
            category.name_ru = new_value
        elif edit_field == 'icon':
            category.icon = new_value
        elif edit_field == 'color':
            category.color = new_value
        
        self.db.commit()
        
        # Clear the waiting state
        context.user_data.pop('waiting_for_category_edit', None)
        context.user_data.pop('edit_category_id', None)
        context.user_data.pop('edit_field', None)
        
        # Send success message
        localized_name = category.get_name(language)
        success_message = get_translation("category_updated", language).format(
            category_name=localized_name
        )
        
        await update.message.reply_text(success_message)
