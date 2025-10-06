"""
Translation system for the Expense Tracker Bot
"""

from typing import Dict, Any

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ru": "Русский"
}

# Supported currencies
SUPPORTED_CURRENCIES = {
    "USD": {"symbol": "USD", "name": "US Dollar", "type": "fiat"},
    "USDT": {"symbol": "USDT", "name": "Tether", "type": "crypto"},
    "ATOM": {"symbol": "ATOM", "name": "Cosmos", "type": "crypto"},
    "UAH": {"symbol": "UAH", "name": "Ukrainian Hryvnia", "type": "fiat"}
}

# Translation strings
TRANSLATIONS = {
    "en": {
        # Main menu
        "welcome_new": """🎉 Welcome to Expense Tracker Bot, {name}!

I'll help you track your income and expenses easily. Here's what you can do:

💰 **Add Transactions**: Record your income and expenses
📊 **View Reports**: See your spending patterns and statistics
🏷️ **Manage Categories**: Create custom categories for better organization
📈 **Analytics**: Get insights into your financial habits

Use the menu below to get started!""",
        
        "welcome_back": """👋 Welcome back, {name}!

Ready to track your expenses? Use the menu below to manage your finances.""",
        
        "main_menu": "",
        "main_menu_button": "🔙 Main Menu",
        "add_transaction": "💰 Add Transaction",
        "view_reports": "📊 Statistics", 
        "manage_categories": "🏷️ Manage Categories",
        "analytics": "📈 Analytics",
        "settings": "⚙️ Settings",
        "balance_settings": "💼 Balance Settings",
        "select_primary_income_category": "Select primary income category:",
        
        # Settings
        "settings_menu": "",
        "language_settings": "🌐 Language Settings",
        "currency_settings": "💱 Currency Settings",
        "back_to_main": "🔙 Back to Main Menu",
        "cancel": "❌ Cancel",
        "yes": "✅ Yes",
        "no": "❌ No",
        "enter": "✅ Enter",
        "operation_cancelled": "❌ Operation cancelled",
        "enter_amount": "Enter amount:",
        "back": "🔙 Back",
        
        # Language
        "select_language": "🌐 **Select Language**\n\nChoose your preferred language:",
        "language_changed": "✅ Language changed to {language_name}!",
        
        # Currency
        "select_currency": "💱 **Select Currency**\n\nChoose your preferred currency:",
        "currency_changed": "✅ Currency changed to {currency_name}!",
        "select_currency_for_transaction": "💱 **Select Currency**\n\nChoose currency for transaction:",
        
        # Transactions
        "add_transaction_menu": "",
        "add_income": "💰 Add Income",
        "add_expense": "💸 Add Expense",
        "recent_transactions": "📋 Recent Transactions",
        "select_category": "Select a category:",
        "enter_amount": "Please enter the amount:",
        "category": "Category",
        "income": "Income",
        "expense": "Expense",
        "transaction_added": """✅ Transaction added successfully!

Amount: {currency_symbol} {amount:,.2f}
Category: {category_icon} {category_name}
Type: {transaction_type}""",
        
        # Categories
        "manage_categories_menu": "",
        "add_new_category": "➕ Add New Category",
        "view_all_categories": "📋 View All Categories",
        "edit_category": "✏️ Edit Category",
        "delete_category": "🗑️ Delete Category",
        "add_category_type": "➕ **Add New Category**\n\nWhat type of category do you want to create?",
        "income_category": "💰 Income Category",
        "expense_category": "💸 Expense Category",
        "enter_category_name": "Please send me the category name:",
        "category_created": "✅ Category '{name}' created successfully!\n\nUse /start to return to the main menu.",
        "category_exists": "Category '{name}' already exists for {type}s.",
        
        # Reports
        "reports_menu": "📊 **Reports & Analytics**\n\nChoose a report type:",
        "monthly_report": "📊 Monthly Report",
        "yearly_report": "📈 Yearly Report",
        "top_expense_categories": "Top Expense Categories",
        "monthly_expense_breakdown": "Monthly Expense Breakdown",
        "category_breakdown": "📋 Category Breakdown",
        "custom_period": "📅 Custom Period",
        
        # Balance
        "balance": "💰 Balance",
        "balance_summary": """💰 **Your Financial Summary**

📈 **Total Income**: {currency_symbol}{income:,.2f}
📉 **Total Expenses**: {currency_symbol}{expenses:,.2f}
💵 **Current Balance**: {currency_symbol}{balance:,.2f}

{balance_status}""",
        "positive_balance": "🎉 You have a positive balance!",
        "negative_balance": "⚠️ You have a negative balance.",
        "zero_balance": "⚖️ Your balance is zero.",
        "currency_breakdown": "Currency Breakdown",
        "transactions": "transactions",
        
        # Help
        "help_text": """🤖 **Expense Tracker Bot Commands**

**Main Commands:**
/start - Start the bot and see main menu
/help - Show this help message
/balance - Show current balance summary

**Transaction Management:**
💰 Add income or expense transactions
📊 View detailed reports and statistics
🏷️ Create and manage custom categories

**Features:**
• Track income and expenses by category
• Monthly and yearly reports
• Visual charts and analytics
• Custom category creation
• Multi-language support
• Multiple currency support

**Quick Tips:**
• Use categories to organize your spending
• Set up recurring transactions for regular income/expenses
• Check reports regularly to understand spending patterns

Need help? Just use /start to see the main menu!""",
        
        # Errors
        "user_not_found": "Please use /start first to initialize your account.",
        "invalid_amount": "Please enter a positive amount.",
        "invalid_number": "Please enter a valid number.",
        "positive_amount": "Please enter a positive amount.",
        "category_not_found": "Category not found.",
        "no_categories": "No categories found. Please create some categories first.",
        "no_transactions": "No transactions found. Start by adding some income or expenses!",
        "unknown_command": "Unknown command. Please use /start to see the main menu.",
        "error_occurred": "An error occurred. Please try again or use /start to restart.",
        
        # Transaction management
        "manage_transactions": "📋 Manage Transactions",
        "select_transaction_to_manage": "Select a transaction to manage:",
        "select_period_to_manage": "Select a period to manage transactions:",
        "transaction_details": "Transaction Details",
        "edit_transaction": "✏️ Edit Transaction",
        "delete_transaction": "🗑️ Delete Transaction",
        "what_to_edit": "What would you like to edit?",
        "amount": "Amount",
        "date": "Date",
        "description": "Description",
        "transaction_deleted": "✅ Transaction deleted successfully!",
        "today": "📅 Today",
        "this_week": "📅 This Week",
        "this_month": "📅 This Month",
        "all_transactions": "📅 All Transactions",
        "all_time": "All Time",
        "no_transactions_in_period": "No transactions found for this period.",
        "back_to_manage": "🔙 Back to Manage",
        "page": "Page",
        "transactions": "transactions",
        "previous": "Previous",
        "next": "Next",
        
        # Weekly reports
        "weekly_report": "📅 Weekly Report",
        "period": "Period",
        "total_income": "Total Income",
        "total_expense": "Total Expense",
        "net_amount": "Net Amount",
        "by_category": "By Category",
        "no_transactions_this_week": "No transactions found for this week.",
        "back_to_reports": "🔙 Back to Reports",
        
        # Date selection
        "select_date": "📅 Select Date",
        "today": "Today",
        "yesterday": "Yesterday",
        "custom_date": "📅 Custom Date",
        "enter_date": "Enter date (DD.MM.YYYY):",
        "invalid_date_format": "Invalid date format. Please use DD.MM.YYYY",
        "future_date_not_allowed": "Future dates are not allowed",
        "date_selected": "Date selected: {date}",
        
        # Analytics
        "analytics_dashboard": "Analytics Dashboard",
        "total_transactions": "Total Transactions",
        "average_amount": "Average Amount",
        "days_active": "Days Active",
        "days": "days",
        "most_used_category": "Most Used Category",
        "times": "times",
        "tips": "Tips",
        "tip_track_daily": "Track daily expenses for better insights",
        "tip_review_monthly": "Review monthly reports regularly",
        "tip_use_categories": "Use categories to identify spending patterns",
        
        # Category management
        "add_category_menu": "➕ **Add New Category**\n\nWhat type of category do you want to create?",
        "add_income_category": "💰 Income Category",
        "add_expense_category": "💸 Expense Category",
        "enter_category_name_en": "💰 **Add Category**\n\nPlease enter the category name in English:",
        "enter_category_name_ru": "💰 **Add Category**\n\nPlease enter the category name in Russian:",
        "invalid_category_name": "Please provide a valid category name.",
        "category_already_exists": "A category with this name already exists.",
        "category_created_success": "Category '{name_en}' / '{name_ru}' created successfully!",
        "use_start_to_return": "Use /start to return to the main menu.",
        "your_categories": "Your Categories",
        "income_categories": "Income Categories",
        "expense_categories": "Expense Categories",
        "no_categories_found": "No categories found. Create some categories to organize your transactions!",
        "select_category_for_expense": "💸 **Add Expense**\n\nSelect a category:",
        "select_category_to_edit": "✏️ **Edit Category**\n\nSelect a category to edit:",
        "select_category_to_delete": "🗑️ **Delete Category**\n\nSelect a category to delete:",
        "edit_not_implemented": "✏️ **Edit Category**\n\nEditing category '{category_name}' is not implemented yet. This feature will be available in future updates.",
        "edit_category_name": "✏️ **Edit Category: {category_name}**\n\nWhat would you like to edit?",
        "edit_name_en": "✏️ Edit English Name",
        "edit_name_ru": "✏️ Edit Russian Name",
        "edit_icon": "🎨 Edit Icon",
        "edit_color": "🎨 Edit Color",
        "enter_new_name_en": "Please enter the new English name for this category:",
        "enter_new_name_ru": "Please enter the new Russian name for this category:",
        "enter_new_icon": "Please enter the new icon (emoji) for this category:",
        "enter_new_color": "Please enter the new color (hex code, e.g., #FF5733) for this category:",
        "category_updated": "✅ **Category Updated**\n\nCategory '{category_name}' has been successfully updated!",
        "invalid_color": "❌ Invalid color format. Please enter a valid hex color code (e.g., #FF5733).",
        
        # Custom period report
        "custom_period_instructions": "📅 **Custom Period Report**\n\nPlease enter the date range in the format:\n`YYYY-MM-DD to YYYY-MM-DD`\n\nExample: `2024-01-01 to 2024-01-31`",
        "no_transactions_period": "📊 **Custom Period Report**\n\nPeriod: {start_date} to {end_date}\n\nNo transactions found in this period.",
        "custom_period_report": "📊 **Custom Period Report**\n\nPeriod: {start_date} to {end_date}\n\n📈 **Summary:**\n• Total Transactions: {total_transactions}\n• Total Income: ${income:,.2f}\n• Total Expenses: ${expenses:,.2f}\n• Balance: ${balance:,.2f}",
        "invalid_date_format": "❌ Invalid date format. Please use the format: `YYYY-MM-DD to YYYY-MM-DD`\n\nExample: `2024-01-01 to 2024-01-31`",
        
        # Add more button
        "add_more": "➕ Add More",
        "category_not_found": "Category not found.",
        "cannot_delete_category_with_transactions": "❌ **Cannot Delete Category**\n\nCategory '{category_name}' has {transaction_count} transactions and cannot be deleted. Please delete or reassign the transactions first.",
        "category_deleted": "✅ **Category Deleted**\n\nCategory '{category_name}' has been successfully deleted.",
        
        # Group functionality
        "group_welcome_new": "🎉 **Welcome to group '{group_title}'!**\n\nThe bot is set up for tracking shared expenses. You can now add transactions and view the group's balance.",
        "group_welcome_existing": "👋 **Welcome to group '{group_title}'!**\n\nYou've joined the group for tracking shared expenses.",
        "group_management_menu": "",
        "add_group_transaction": "💰 Add Transaction",
        "view_group_balance": "📊 Group Balance",
        "group_reports": "📈 Group Reports",
        "group_settings": "⚙️ Group Settings",
        "create_new_group": "➕ Create New Group",
        "select_transaction_type": "💰 **Add Group Transaction**\n\nSelect transaction type:",
        "no_group_transactions": "📊 **Group Balance**\n\nNo transactions in the group yet. Start by adding income or expenses!",
        "group_balance_summary": "📊 **Group Balance: {group_title}**\n\n💰 **Total Income:** {total_income:,.2f} {currency}\n💸 **Total Expenses:** {total_expenses:,.2f} {currency}\n📈 **Balance:** {balance:,.2f} {currency}",
        "role_admin": "Admin",
        "role_member": "Member",
        "role_viewer": "Viewer",
        "no_income_categories": "No income categories found for this group.",
        "no_expense_categories": "No expense categories found for this group.",
        "select_income_category": "💰 **Add Income to Group**\n\nSelect income category:",
        "select_expense_category": "💸 **Add Expense to Group**\n\nSelect expense category:",
        "enter_amount_for_category": "💰 **Enter Amount**\n\nEnter amount for category: {category_name}",
        "group_transaction_added": "{type_emoji} **Transaction Added!**\n\n**Amount:** {amount:,.2f} {currency}\n**Category:** {category_name}\n**Group:** {group_title}\n\nTransaction has been added to the group's balance."
    },
    
    "ru": {
        # Main menu
        "welcome_new": """🎉 Добро пожаловать в Expense Tracker Bot, {name}!

Я помогу вам легко отслеживать доходы и расходы. Вот что вы можете делать:

💰 **Добавить транзакции**: Записывайте доходы и расходы
📊 **Просмотр отчетов**: Смотрите статистику и паттерны трат
🏷️ **Управление категориями**: Создавайте пользовательские категории
📈 **Аналитика**: Получайте инсайты о ваших финансовых привычках

Используйте меню ниже, чтобы начать!""",
        
        "welcome_back": """👋 С возвращением, {name}!

Готовы отслеживать расходы? Используйте меню ниже для управления финансами.""",
        
        "main_menu": "",
        "main_menu_button": "🔙 Главное меню",
        "add_transaction": "💰 Добавить транзакцию",
        "view_reports": "📊 Статистика",
        "manage_categories": "🏷️ Управление категориями",
        "analytics": "📈 Аналитика",
        "settings": "⚙️ Настройки",
        "balance_settings": "💼 Настройки баланса",
        "select_primary_income_category": "Выберите основную категорию дохода:",
        
        # Settings
        "settings_menu": "",
        "language_settings": "🌐 Настройки языка",
        "currency_settings": "💱 Настройки валюты",
        "back_to_main": "🔙 Назад в главное меню",
        "cancel": "❌ Отмена",
        "yes": "✅ Да",
        "no": "❌ Нет",
        "enter": "✅ Ввод",
        "operation_cancelled": "❌ Операция отменена",
        "enter_amount": "Введите сумму:",
        "back": "🔙 Назад",
        
        # Language
        "select_language": "🌐 **Выбор языка**\n\nВыберите предпочитаемый язык:",
        "language_changed": "✅ Язык изменен на {language_name}!",
        
        # Currency
        "select_currency": "💱 **Выбор валюты**\n\nВыберите предпочитаемую валюту:",
        "currency_changed": "✅ Валюта изменена на {currency_name}!",
        "select_currency_for_transaction": "💱 **Выбор валюты**\n\nВыберите валюту для транзакции:",
        
        # Transactions
        "add_transaction_menu": "",
        "add_income": "💰 Добавить доход",
        "add_expense": "💸 Добавить расход",
        "recent_transactions": "📋 Последние транзакции",
        "select_category": "Выберите категорию:",
        "enter_amount": "Пожалуйста, введите сумму:",
        "category": "Категория",
        "income": "Доход",
        "expense": "Расход",
        "transaction_added": """✅ Транзакция успешно добавлена!

Сумма: {currency_symbol} {amount:,.2f}
Категория: {category_icon} {category_name}
Тип: {transaction_type}""",
        
        # Categories
        "manage_categories_menu": "",
        "add_new_category": "➕ Добавить новую категорию",
        "view_all_categories": "📋 Просмотр всех категорий",
        "edit_category": "✏️ Редактировать категорию",
        "delete_category": "🗑️ Удалить категорию",
        "add_category_type": "➕ **Добавить новую категорию**\n\nКакой тип категории вы хотите создать?",
        "income_category": "💰 Категория доходов",
        "expense_category": "💸 Категория расходов",
        "enter_category_name": "Пожалуйста, отправьте мне название категории:",
        "category_created": "✅ Категория '{name}' успешно создана!\n\nИспользуйте /start для возврата в главное меню.",
        "category_exists": "Категория '{name}' уже существует для {type}ов.",
        
        # Reports
        "reports_menu": "📊 **Отчеты и аналитика**\n\nВыберите тип отчета:",
        "monthly_report": "📊 Месячный отчет",
        "yearly_report": "📈 Годовой отчет",
        "top_expense_categories": "Топ категорий расходов",
        "monthly_expense_breakdown": "Помесячная разбивка расходов",
        "category_breakdown": "📋 Разбивка по категориям",
        "custom_period": "📅 Произвольный период",
        
        # Balance
        "balance": "💰 Баланс",
        "balance_summary": """💰 **Ваша финансовая сводка**

📈 **Общий доход**: {currency_symbol}{income:,.2f}
📉 **Общие расходы**: {currency_symbol}{expenses:,.2f}
💵 **Текущий баланс**: {currency_symbol}{balance:,.2f}

{balance_status}""",
        "positive_balance": "🎉 У вас положительный баланс!",
        "negative_balance": "⚠️ У вас отрицательный баланс.",
        "zero_balance": "⚖️ Ваш баланс равен нулю.",
        "currency_breakdown": "Разбивка по валютам",
        "transactions": "транзакций",
        
        # Help
        "help_text": """🤖 **Команды Expense Tracker Bot**

**Основные команды:**
/start - Запустить бота и показать главное меню
/help - Показать это сообщение помощи
/balance - Показать текущую сводку баланса

**Управление транзакциями:**
💰 Добавлять транзакции доходов и расходов
📊 Просматривать детальные отчеты и статистику
🏷️ Создавать и управлять пользовательскими категориями

**Возможности:**
• Отслеживание доходов и расходов по категориям
• Месячные и годовые отчеты
• Визуальные графики и аналитика
• Создание пользовательских категорий
• Поддержка нескольких языков
• Поддержка нескольких валют

**Быстрые советы:**
• Используйте категории для организации трат
• Настройте регулярные транзакции для постоянных доходов/расходов
• Регулярно проверяйте отчеты для понимания паттернов трат

Нужна помощь? Просто используйте /start для просмотра главного меню!""",
        
        # Additional missing keys
        "add_transaction_menu": "",
        "select_currency_for_transaction": "💱 **Выбор валюты**\n\nВыберите валюту для транзакции:",
        
        # Analytics
        "analytics_dashboard": "Панель аналитики",
        "total_transactions": "Всего транзакций",
        "average_amount": "Средняя сумма",
        "days_active": "Дней активности",
        "days": "дней",
        "most_used_category": "Самая используемая категория",
        "times": "раз",
        "tips": "Советы",
        "tip_track_daily": "Отслеживайте ежедневные расходы для лучших инсайтов",
        "tip_review_monthly": "Регулярно просматривайте месячные отчеты",
        "tip_use_categories": "Используйте категории для выявления паттернов трат",
        
        # Category management
        "add_category_menu": "➕ **Добавить категорию**\n\nКакой тип категории вы хотите создать?",
        "add_income_category": "💰 Категория дохода",
        "add_expense_category": "💸 Категория расхода",
        "enter_category_name_en": "💰 **Добавить категорию**\n\nВведите название категории на английском:",
        "enter_category_name_ru": "💰 **Добавить категорию**\n\nВведите название категории на русском:",
        "invalid_category_name": "Пожалуйста, введите корректное название категории.",
        "category_already_exists": "Категория с таким названием уже существует.",
        "category_created_success": "Категория '{name_en}' / '{name_ru}' успешно создана!",
        "use_start_to_return": "Используйте /start для возврата в главное меню.",
        "your_categories": "Ваши категории",
        "income_categories": "Категории доходов",
        "expense_categories": "Категории расходов",
        "no_categories_found": "Категории не найдены. Создайте категории для организации транзакций!",
        "select_category_for_expense": "💸 **Добавить расход**\n\nВыберите категорию:",
        "select_category_to_edit": "✏️ **Редактировать категорию**\n\nВыберите категорию для редактирования:",
        "select_category_to_delete": "🗑️ **Удалить категорию**\n\nВыберите категорию для удаления:",
        "edit_not_implemented": "✏️ **Редактировать категорию**\n\nРедактирование категории '{category_name}' пока не реализовано. Эта функция будет доступна в будущих обновлениях.",
        "edit_category_name": "✏️ **Редактировать категорию: {category_name}**\n\nЧто вы хотите изменить?",
        "edit_name_en": "✏️ Изменить английское название",
        "edit_name_ru": "✏️ Изменить русское название",
        "edit_icon": "🎨 Изменить иконку",
        "edit_color": "🎨 Изменить цвет",
        "enter_new_name_en": "Пожалуйста, введите новое английское название для этой категории:",
        "enter_new_name_ru": "Пожалуйста, введите новое русское название для этой категории:",
        "enter_new_icon": "Пожалуйста, введите новую иконку (эмодзи) для этой категории:",
        "enter_new_color": "Пожалуйста, введите новый цвет (hex код, например, #FF5733) для этой категории:",
        "category_updated": "✅ **Категория обновлена**\n\nКатегория '{category_name}' была успешно обновлена!",
        "invalid_color": "❌ Неверный формат цвета. Пожалуйста, введите корректный hex код цвета (например, #FF5733).",
        
        # Custom period report
        "custom_period_instructions": "📅 **Отчет за произвольный период**\n\nПожалуйста, введите диапазон дат в формате:\n`YYYY-MM-DD to YYYY-MM-DD`\n\nПример: `2024-01-01 to 2024-01-31`",
        "no_transactions_period": "📊 **Отчет за произвольный период**\n\nПериод: {start_date} по {end_date}\n\nВ этом периоде транзакции не найдены.",
        "custom_period_report": "📊 **Отчет за произвольный период**\n\nПериод: {start_date} по {end_date}\n\n📈 **Сводка:**\n• Всего транзакций: {total_transactions}\n• Общий доход: ${income:,.2f}\n• Общие расходы: ${expenses:,.2f}\n• Баланс: ${balance:,.2f}",
        "invalid_date_format": "❌ Неверный формат даты. Пожалуйста, используйте формат: `YYYY-MM-DD to YYYY-MM-DD`\n\nПример: `2024-01-01 to 2024-01-31`",
        
        # Add more button
        "add_more": "➕ Добавить еще",
        "category_not_found": "Категория не найдена.",
        "cannot_delete_category_with_transactions": "❌ **Нельзя удалить категорию**\n\nКатегория '{category_name}' содержит {transaction_count} транзакций и не может быть удалена. Сначала удалите или переназначьте транзакции.",
        "category_deleted": "✅ **Категория удалена**\n\nКатегория '{category_name}' была успешно удалена.",
        
        # Group functionality
        "group_welcome_new": "🎉 **Добро пожаловать в группу '{group_title}'!**\n\nБот настроен для отслеживания совместных расходов. Теперь вы можете добавлять транзакции и просматривать общий баланс группы.",
        "group_welcome_existing": "👋 **Добро пожаловать в группу '{group_title}'!**\n\nВы присоединились к группе для отслеживания совместных расходов.",
        "group_management_menu": "",
        "add_group_transaction": "💰 Добавить транзакцию",
        "view_group_balance": "📊 Баланс группы",
        "group_reports": "📈 Отчеты группы",
        "group_settings": "⚙️ Настройки группы",
        "create_new_group": "➕ Создать новую группу",
        "select_transaction_type": "💰 **Добавить транзакцию в группу**\n\nВыберите тип транзакции:",
        "no_group_transactions": "📊 **Баланс группы**\n\nВ группе пока нет транзакций. Начните с добавления доходов или расходов!",
        "group_balance_summary": "📊 **Баланс группы: {group_title}**\n\n💰 **Общий доход:** {total_income:,.2f} {currency}\n💸 **Общие расходы:** {total_expenses:,.2f} {currency}\n📈 **Баланс:** {balance:,.2f} {currency}",
            "role_admin": "Администратор",
            "role_member": "Участник",
            "role_viewer": "Наблюдатель",
            "no_income_categories": "В этой группе нет категорий доходов.",
            "no_expense_categories": "В этой группе нет категорий расходов.",
            "select_income_category": "💰 **Добавить доход в группу**\n\nВыберите категорию дохода:",
            "select_expense_category": "💸 **Добавить расход в группу**\n\nВыберите категорию расхода:",
            "enter_amount_for_category": "💰 **Введите сумму**\n\nВведите сумму для категории: {category_name}",
            "group_transaction_added": "{type_emoji} **Транзакция добавлена!**\n\n**Сумма:** {amount:,.2f} {currency}\n**Категория:** {category_name}\n**Группа:** {group_title}\n\nТранзакция добавлена в баланс группы.",
        
        # Errors
        "user_not_found": "Пожалуйста, сначала используйте /start для инициализации аккаунта.",
        "invalid_amount": "Пожалуйста, введите положительную сумму.",
        "invalid_number": "Пожалуйста, введите корректное число.",
        "positive_amount": "Пожалуйста, введите положительное число.",
        "category_not_found": "Категория не найдена.",
        "no_categories": "Категории не найдены. Пожалуйста, сначала создайте категории.",
        "no_transactions": "Транзакции не найдены. Начните с добавления доходов или расходов!",
        "unknown_command": "Неизвестная команда. Пожалуйста, используйте /start для просмотра главного меню.",
        "error_occurred": "Произошла ошибка. Пожалуйста, попробуйте снова или используйте /start для перезапуска.",
        
        # Transaction management
        "manage_transactions": "📋 Управление транзакциями",
        "select_transaction_to_manage": "Выберите транзакцию для управления:",
        "select_period_to_manage": "Выберите период для управления транзакциями:",
        "transaction_details": "Детали транзакции",
        "edit_transaction": "✏️ Редактировать транзакцию",
        "delete_transaction": "🗑️ Удалить транзакцию",
        "what_to_edit": "Что вы хотите отредактировать?",
        "amount": "Сумма",
        "date": "Дата",
        "description": "Описание",
        "transaction_deleted": "✅ Транзакция успешно удалена!",
        "today": "📅 Сегодня",
        "this_week": "📅 Эта неделя",
        "this_month": "📅 Этот месяц",
        "all_transactions": "📅 Все транзакции",
        "all_time": "За все время",
        "no_transactions_in_period": "Транзакции за этот период не найдены.",
        "back_to_manage": "🔙 Назад к управлению",
        "page": "Страница",
        "transactions": "транзакций",
        "previous": "Назад",
        "next": "Далее",
        
        # Weekly reports
        "weekly_report": "📅 Недельный отчет",
        "period": "Период",
        "total_income": "Общий доход",
        "total_expense": "Общие расходы",
        "net_amount": "Чистая сумма",
        "by_category": "По категориям",
        "no_transactions_this_week": "Транзакции за эту неделю не найдены.",
        "back_to_reports": "🔙 Назад к отчетам",
        
        # Date selection
        "select_date": "📅 Выбрать дату",
        "today": "Сегодня",
        "yesterday": "Вчера",
        "custom_date": "📅 Другая дата",
        "enter_date": "Введите дату (ДД.ММ.ГГГГ):",
        "invalid_date_format": "Неверный формат даты. Используйте ДД.ММ.ГГГГ",
        "future_date_not_allowed": "Будущие даты не разрешены",
        "date_selected": "Дата выбрана: {date}"
    }
}

def get_translation(key: str, language: str = "en", **kwargs) -> str:
    """Get translation for a key in specified language"""
    if language not in TRANSLATIONS:
        language = "en"
    
    translation = TRANSLATIONS[language].get(key, TRANSLATIONS["en"].get(key, key))
    
    # Format with provided kwargs
    try:
        return translation.format(**kwargs)
    except (KeyError, ValueError):
        return translation

def get_currency_symbol(currency_code: str) -> str:
    """Get currency symbol for currency code"""
    return SUPPORTED_CURRENCIES.get(currency_code, {}).get("symbol", "$")

def get_currency_name(currency_code: str, language: str = "en") -> str:
    """Get currency name for currency code"""
    currency_info = SUPPORTED_CURRENCIES.get(currency_code, {})
    return currency_info.get("name", "US Dollar")

def format_amount(amount: float, currency_code: str) -> str:
    """Format amount with currency symbol"""
    symbol = get_currency_symbol(currency_code)
    return f"{symbol} {amount:,.2f}"
