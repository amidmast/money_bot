import logging
import os
import re
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config.settings import settings
from src.handlers.user import UserHandler
from src.handlers.category import CategoryHandler
from src.handlers.transaction import TransactionHandler
from src.handlers.report import ReportHandler
from src.handlers.settings import SettingsHandler
from src.utils.speech import transcribe_bytes
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from src.models.category import CategoryType

class TokenFilter(logging.Filter):
    """Filter to hide bot token from logs"""
    def filter(self, record):
        if hasattr(record, 'msg'):
            # Hide bot token from URLs
            record.msg = re.sub(r'bot\d+:[A-Za-z0-9_-]+', 'bot***TOKEN***', str(record.msg))
            record.msg = re.sub(r'bot8223285085:[A-Za-z0-9_-]+', 'bot***TOKEN***', str(record.msg))
        return True

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, settings.LOG_LEVEL)
)

# Add token filter to all loggers and set httpx to WARNING level
for logger_name in ['httpx', 'telegram', 'telegram.ext']:
    logger_obj = logging.getLogger(logger_name)
    logger_obj.addFilter(TokenFilter())
    if logger_name == 'httpx':
        logger_obj.setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

class ExpenseTrackerBot:
    def __init__(self):
        self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        self.user_handler = UserHandler()
        self.category_handler = CategoryHandler()
        self.transaction_handler = TransactionHandler()
        self.report_handler = ReportHandler()
        self.settings_handler = SettingsHandler()
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup all bot handlers"""
        
        # Command handlers - allow in groups
        self.application.add_handler(CommandHandler("start", self._handle_start_command))
        self.application.add_handler(CommandHandler("add", self._handle_add_command))
        self.application.add_handler(CommandHandler("test", self._handle_test_command))
        self.application.add_handler(CommandHandler("help", self.user_handler.handle_help))
        self.application.add_handler(CommandHandler("balance", self.user_handler.handle_balance))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self._handle_callback_query))
        
        # Message handlers for text input
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text_message))
        
        # Voice/audio handler (only if enabled)
        if settings.ENABLE_VOICE_INPUT:
            self.application.add_handler(MessageHandler((filters.VOICE | filters.AUDIO) & ~filters.COMMAND, self._handle_voice_message))
            logger.info("Voice input enabled (Google Cloud Speech-to-Text)")
        else:
            logger.info("Voice input disabled")
        
        # Debug handler for all messages
        self.application.add_handler(MessageHandler(filters.ALL, self._handle_debug_message))
    
    async def _handle_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command for both users and groups"""
        logger.info(f"Start command received: chat_id={update.message.chat.id}, type={update.message.chat.type}, title={update.message.chat.title}")
        
        # Route to user handler (now handles both users and groups)
        await self.user_handler.handle_start(update, context)
    
    async def _handle_test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /test command for debugging"""
        chat = update.message.chat
        logger.info(f"Test command received: chat_id={chat.id}, type={chat.type}, title={chat.title}")
        
        response = f"✅ **Тест успешен!**\n\n"
        response += f"📊 **Информация о чате:**\n"
        response += f"• ID: `{chat.id}`\n"
        response += f"• Тип: `{chat.type}`\n"
        response += f"• Название: `{chat.title or 'Не указано'}`\n"
        response += f"• Пользователь: `{update.message.from_user.first_name}`\n\n"
        response += f"🤖 **Бот работает корректно!**"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    
    async def _handle_add_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /add command to open Add Expense flow directly"""
        # Route directly to Add Expense menu
        await self.transaction_handler.handle_add_expense(update, context)
    
    async def _handle_debug_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Debug handler for all messages"""
        if update.message:
            chat = update.message.chat
            print(f"DEBUG: Message received: chat_id={chat.id}, type={chat.type}, title={chat.title}, text='{update.message.text}'")
            logger.info(f"Message received: chat_id={chat.id}, type={chat.type}, title={chat.title}, text='{update.message.text}'")
    
    async def _handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        try:
            # Main menu handlers
            if callback_data == "main_menu":
                await self.user_handler.handle_start(update, context)
            
            # Transaction handlers
            elif callback_data == "add_transaction":
                await self.transaction_handler.handle_add_transaction(update, context)
            elif callback_data == "add_income":
                await self.transaction_handler.handle_add_income(update, context)
            elif callback_data == "add_expense":
                await self.transaction_handler.handle_add_expense(update, context)
            elif callback_data == "recent_transactions":
                await self.transaction_handler.handle_recent_transactions(update, context)
            elif callback_data == "manage_transactions":
                await self.transaction_handler.handle_manage_transactions(update, context)
            elif callback_data.startswith("manage_transactions_"):
                await self.transaction_handler.handle_manage_transactions_period(update, context)
            elif callback_data.startswith("manage_transaction_"):
                await self.transaction_handler.handle_manage_specific_transaction(update, context)
            elif callback_data.startswith("edit_transaction_"):
                await self.transaction_handler.handle_edit_transaction(update, context)
            elif callback_data.startswith("delete_transaction_"):
                await self.transaction_handler.handle_delete_transaction(update, context)
            elif callback_data.startswith("select_category_"):
                await self.transaction_handler.handle_select_category(update, context)
            # Currency selection removed from add flow; currency changes only via manage/edit
            elif callback_data.startswith("select_date_"):
                await self.transaction_handler.handle_select_date(update, context)
            
            # Amount input keyboard handlers
            elif callback_data.startswith("amount_"):
                await self.transaction_handler.handle_amount_input(update, context)
            
            # Category handlers
            elif callback_data == "manage_categories":
                await self.category_handler.handle_manage_categories(update, context)
            elif callback_data == "add_category":
                await self.category_handler.handle_add_category(update, context)
            elif callback_data == "add_income_category":
                await self.category_handler.handle_add_income_category(update, context)
            elif callback_data == "add_expense_category":
                await self.category_handler.handle_add_expense_category(update, context)
            elif callback_data == "view_categories":
                await self.category_handler.handle_view_categories(update, context)
            elif callback_data == "edit_category":
                await self.category_handler.handle_edit_category(update, context)
            elif callback_data == "delete_category":
                await self.category_handler.handle_delete_category(update, context)
            elif callback_data.startswith("edit_category_"):
                await self.category_handler.handle_edit_specific_category(update, context)
            elif callback_data.startswith("delete_category_"):
                await self.category_handler.handle_delete_specific_category(update, context)
            elif callback_data.startswith("edit_name_en_"):
                await self.category_handler.handle_edit_name_en(update, context)
            elif callback_data.startswith("edit_name_ru_"):
                await self.category_handler.handle_edit_name_ru(update, context)
            elif callback_data.startswith("edit_icon_"):
                await self.category_handler.handle_edit_icon(update, context)
            elif callback_data.startswith("edit_color_"):
                await self.category_handler.handle_edit_color(update, context)
            
            # Report handlers
            elif callback_data == "view_reports":
                await self.report_handler.handle_view_reports(update, context)
            elif callback_data == "weekly_report":
                await self.report_handler.handle_weekly_report(update, context)
            elif callback_data == "balance_report":
                await self.report_handler.handle_balance_report(update, context)
            elif callback_data == "monthly_report":
                await self.report_handler.handle_monthly_report(update, context)
            elif callback_data == "yearly_report":
                await self.report_handler.handle_yearly_report(update, context)
            elif callback_data == "category_breakdown":
                await self.report_handler.handle_category_breakdown(update, context)
            elif callback_data == "analytics":
                await self.report_handler.handle_analytics(update, context)
            elif callback_data == "custom_period":
                await self.report_handler.handle_custom_period_report(update, context)
            
            # Settings handlers
            elif callback_data == "settings":
                await self.settings_handler.handle_settings_menu(update, context)
            elif callback_data == "language_settings":
                await self.settings_handler.handle_language_settings(update, context)
            elif callback_data == "currency_settings":
                await self.settings_handler.handle_currency_settings(update, context)
            elif callback_data == "balance_settings":
                await self.settings_handler.handle_balance_settings(update, context)
            elif callback_data.startswith("set_primary_income_"):
                await self.settings_handler.handle_set_primary_income(update, context)
            elif callback_data.startswith("set_language_"):
                await self.settings_handler.handle_set_language(update, context)
            elif callback_data.startswith("set_currency_"):
                await self.settings_handler.handle_set_currency(update, context)
            
            
            else:
                await query.edit_message_text("Unknown command. Please use /start to see the main menu.")
        
        except Exception as e:
            logger.error(f"Error handling callback query {callback_data}: {e}")
            await query.edit_message_text("An error occurred. Please try again or use /start to restart.")
    
    async def _handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (for category names, amounts, etc.)"""
        try:
            # Check if we're waiting for category name input
            if context.user_data.get('waiting_for_category_name'):
                await self.category_handler.handle_category_name_input(update, context)
            
            # Amount input is now handled via InlineKeyboard callback queries
            # No need to handle text messages for amount input
            
            # Check if we're waiting for category edit input
            elif context.user_data.get('waiting_for_category_edit'):
                await self.category_handler.handle_category_edit_input(update, context)
            
            # Check if we're waiting for custom period input
            elif context.user_data.get('waiting_for_custom_period'):
                await self.report_handler.handle_custom_period_input(update, context)
            
            # Check if we're waiting for custom date input
            elif context.user_data.get('waiting_for_custom_date'):
                await self.transaction_handler.handle_custom_date_input(update, context)
            
            else:
                # Ignore all other text messages - don't respond
                # This prevents the bot from responding to random text
                pass
        
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            # Don't send error message for ignored text
    
    async def _handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice/audio messages: transcribe and jump into Add Expense flow."""
        try:
            file_id = None
            if update.message.voice:
                file_id = update.message.voice.file_id
            elif update.message.audio:
                file_id = update.message.audio.file_id
            if not file_id:
                return

            tg_file = await self.application.bot.get_file(file_id)
            file_bytes = await tg_file.download_as_bytearray()

            langs_env = os.getenv("SPEECH_RECOGNITION_LANGUAGES", "ru-RU,en-US,uk-UA")
            languages = [s.strip() for s in langs_env.split(',') if s.strip()]
            target_lang = os.getenv("SPEECH_TARGET_LANGUAGE", "ru-RU")

            text = transcribe_bytes(bytes(file_bytes), languages, target_lang)
            if not text:
                await update.message.reply_text("Не удалось распознать голосовое сообщение.")
                return
            # Log recognized text for diagnostics
            try:
                logger.info(f"Voice recognized (chat_id={update.message.chat.id}): {text}")
            except Exception:
                pass

            # Save recognized text to use as description later
            context.user_data['voice_description'] = text

            # Try to extract amount; support thousand markers ("тыс", "тысяч", "тисяч", "thousand", "k", "к")
            amount_value_detected = None
            text_lower = text.lower()
            thousand_marker_pattern = r"(тыс\.?|тысяч|тисяч|thousand|\bk\b|\bк\b)"
            # Prefer number followed by thousand marker
            m_thousand = re.search(rf"(\d+(?:[\s\u00A0]?\d*(?:[\.,]\d{{1,2}})?)?)\s*{thousand_marker_pattern}", text_lower)
            if m_thousand:
                raw_num = m_thousand.group(1)
                normalized_num = re.sub(r"[\s\u00A0]", "", raw_num).replace(",", ".")
                try:
                    amount_value_detected = float(normalized_num) * 1000.0
                    logger.info(f"Voice amount: detected thousand marker, multiplied -> {amount_value_detected}")
                except Exception:
                    amount_value_detected = None
            if amount_value_detected is None:
                # Fallback: plain number
                amount_match = re.search(r"(\d+[\s\u00A0]?\d*(?:[\.,]\d{1,2})?)", text)
                if amount_match:
                    raw_amount = amount_match.group(1)
                    normalized = re.sub(r"[\s\u00A0]", "", raw_amount).replace(",", ".")
                    try:
                        amount_value_detected = float(normalized)
                    except Exception:
                        amount_value_detected = None
            if amount_value_detected is not None and amount_value_detected > 0:
                # Format amount buffer nicely (max 2 decimals, no trailing zeros)
                formatted = ("{:.2f}".format(amount_value_detected)).rstrip('0').rstrip('.')
                if re.match(r"^\d+(?:\.\d{1,2})?$", formatted):
                    context.user_data['amount_buffer'] = formatted
                    context.user_data['voice_amount'] = formatted

            # Try to auto-pick expense category by name in recognized text
            try:
                category = self.transaction_handler.find_expense_category_by_text(update, text)
            except Exception:
                category = None

            if category and context.user_data.get('amount_buffer'):
                # If we have both category and amount, try to detect date and create immediately
                text_norm = text.lower()
                today = datetime.now().date()
                if any(k in text_norm for k in ["сегодня", "today", "сьогодні"]):
                    picked_date = today
                elif any(k in text_norm for k in ["вчера", "yesterday", "вчора"]):
                    picked_date = today - timedelta(days=1)
                else:
                    picked_date = today

                try:
                    amount_value = float(context.user_data['amount_buffer'].replace(',', '.'))
                except Exception:
                    amount_value = None

                if amount_value is not None and amount_value > 0:
                    await self.transaction_handler.create_transaction_direct(
                        update,
                        context,
                        category_id=category.id,
                        amount=amount_value,
                        selected_date=picked_date,
                        description=text
                    )
                    return

            # Fallbacks: start guided flow with a short recognition summary
            try:
                amount_value_preview = context.user_data.get('amount_buffer') or '-'
                date_hint = 'сегодня' if 'сегодня' in text.lower() or 'today' in text.lower() or 'сьогодні' in text.lower() else ('вчера' if 'вчера' in text.lower() or 'yesterday' in text.lower() or 'вчора' in text.lower() else '-')
                cat_name = category.get_name(context.user_data.get('preferred_language', 'ru')) if category else '-'
                await update.message.reply_text(
                    f"Распознано:\nКатегория: {cat_name}\nСумма: {amount_value_preview}\nДата: {date_hint}\n\nПродолжим вручную.")
            except Exception:
                pass

            if category:
                await self.transaction_handler.start_expense_with_category_id(update, context, category.id)
            else:
                await self.transaction_handler.handle_add_expense(update, context)
        except Exception as e:
            logger.error(f"Error handling voice message: {e}")
            await update.message.reply_text("Произошла ошибка при распознавании. Попробуйте еще раз.")
    
    def run(self):
        """Run the bot"""
        logger.info("Starting Expense Tracker Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main function to run the bot"""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    bot = ExpenseTrackerBot()
    bot.run()

if __name__ == "__main__":
    main()
