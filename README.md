# 💰 Expense Tracker Telegram Bot

A comprehensive Telegram bot for tracking income and expenses with PostgreSQL backend, featuring category management, detailed reporting, and analytics.

## 📸 Screenshots

### Main Menu
<img src="docs/images/main-menu.png" width="300" alt="Main Menu">

*Main bot interface with quick access to all features*

### Adding Transaction
<img src="docs/images/add-transaction.png" width="300" alt="Add Transaction">
<img src="docs/images/add-transaction-2.png" width="300" alt="Add Transaction">
<img src="docs/images/add-transaction-3.png" width="300" alt="Add Transaction">

*Simple transaction entry with category selection and amount input*

### Voice Input
*Voice-msg: "Здоровье одна тысяча двести"*
<img src="docs/images/voice-input.png" width="300" alt="Voice Transaction">

*Voice message recognition with auto-detection of category, amount, and date*

### Statistics & Balance
<img src="docs/images/statistics.png" width="300" alt="Statistics">

*Comprehensive financial reports and balance overview*

---

## 🚀 Features

### Core Functionality
- **💰 Income & Expense Tracking**: Record and categorize all your financial transactions
- **🏷️ Custom Categories**: Create personalized income and expense categories
- **📊 Detailed Reports**: Monthly and yearly financial reports with insights
- **📈 Analytics Dashboard**: Track spending patterns and financial trends
- **💵 Balance Tracking**: Real-time balance calculation and summaries
- **🌐 Multi-Language Support**: Choose between English and Russian interfaces
- **💱 Multi-Currency Support**: Support for fiat and cryptocurrency transactions
- **🔄 Real-time Exchange Rates**: Automatic currency conversion and rate updates

### Advanced Features
- **🎨 Category Customization**: Icons, colors, and descriptions for categories
- **📅 Date-based Filtering**: View transactions by specific time periods
- **📋 Transaction History**: Browse recent transactions with full details
- **🔍 Category Breakdown**: Detailed analysis of spending by category
- **📊 Visual Reports**: Weekly, monthly, yearly expense breakdowns, balance view
- **⚡ Real-time Updates**: Instant balance and transaction updates
- **🌍 Supported Currencies**: USD, USDT, ATOM, UAH
- **🔄 Exchange Rate Updates**: Automatic hourly updates from multiple APIs
- **💱 Currency Conversion**: Real-time conversion between all supported currencies
- **🎤 Voice Transactions**: Add expenses via voice messages (Google Cloud Speech-to-Text)

### User Experience
- **🤖 Intuitive Interface**: Easy-to-use inline keyboard navigation
- **📱 Mobile Optimized**: Perfect for mobile Telegram usage
- **🔄 Quick Actions**: Fast transaction entry and category management
- **💾 Persistent Storage**: All data securely stored in PostgreSQL
- **🔒 User Isolation**: Each user's data is completely separate
- **🌐 Language Selection**: Choose your preferred language (English/Russian)
- **💱 Currency Selection**: Select currency for each transaction
- **📊 Unified Balance**: View all balances converted to your preferred currency

## 🛠️ Quick Start (Docker - Recommended)

### Prerequisites
- Docker and Docker Compose installed
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- (Optional) Google Cloud credentials for voice input

### Step 1: Get Your Bot Token
1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow instructions
3. Copy your bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Clone and Configure
```bash
# Clone repository
git clone <repository-url>
cd money_bot

# Create environment file
cp env.example .env

# Edit .env and add your bot token
nano .env
# Set: TELEGRAM_BOT_TOKEN=your_token_here
```

### Step 3: (Optional) Enable Voice Input
If you want voice transaction support via Google Cloud Speech-to-Text:

1. Create a Google Cloud project and enable Speech-to-Text API
2. Create a service account and download `credentials.json`
3. Place `credentials.json` in the project root
4. Update `.env`:
```env
ENABLE_VOICE_INPUT=True
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
SPEECH_RECOGNITION_LANGUAGES=ru-RU,en-US,uk-UA
SPEECH_TARGET_LANGUAGE=ru-RU
```

> **Note:** If you don't need voice input, leave `ENABLE_VOICE_INPUT=False` (default) and skip this step entirely.

### Step 4: Start the Bot
```bash
# Make scripts executable
chmod +x docker-start.sh docker-stop.sh

# Start everything (builds images, creates database, runs migrations)
./docker-start.sh
```

That's it! Your bot is now running. Find it on Telegram and send `/start`.

### Step 5: Stop the Bot
```bash
./docker-stop.sh
```

---

## 🛠️ Manual Installation (Without Docker)

### Prerequisites
- Python 3.11 or higher
- PostgreSQL 12 or higher
- Telegram Bot Token

### 1. Clone the Repository
```bash
git clone <repository-url>
cd money_bot
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database
```sql
CREATE DATABASE expense_tracker;
CREATE USER expense_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE expense_tracker TO expense_user;
```

### 5. Configure Environment
```bash
cp env.example .env
nano .env
```

Edit `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_URL=postgresql://expense_user:your_password@localhost:5432/expense_tracker
DB_HOST=localhost
DB_PORT=5432
DB_NAME=expense_tracker
DB_USER=expense_user
DB_PASSWORD=your_password
DEBUG=True
LOG_LEVEL=INFO
```

### 6. Initialize Database
```bash
# Run all migrations and create default categories
python migrations.py
```

### 7. Run the Bot
```bash
python main.py
```

Or use the startup script:
```bash
chmod +x start.sh
./start.sh
```

## 📱 Usage

### Getting Started
1. Start a conversation with your bot on Telegram
2. Send `/start` to initialize your account
3. Choose your language (English/Russian/Ukrainian)
4. Set your preferred currency (USD/UAH/USDT/ATOM)
5. The bot creates default categories automatically
6. Use the inline keyboard to navigate

### Commands
- `/start` - Initialize bot and show main menu
- `/help` - Display help information
- `/balance` - Show current financial summary
- `/add` - Quick add expense

### Main Features

#### 💰 Adding Transactions
**Via Menu:**
1. Click "📝 Добавить транзакцию" from main menu
2. Choose "💰 Добавить доход" or "💸 Добавить расход"
3. Select a category
4. Choose date (today/yesterday/custom)
5. Enter amount using inline keyboard
6. Transaction saved automatically

**Via Voice (if enabled):**
1. Send a voice message: "здоровье 380 гривен сегодня"
2. Bot auto-detects category, amount, and date
3. Transaction created instantly
4. Supports: Russian, English, Ukrainian
5. Recognizes "тысяч/thousand/k" for thousands

#### 🏷️ Managing Categories
1. Click "🏷️ Управление категориями" from main menu
2. Add/edit/delete income and expense categories
3. Customize icons, names (multilingual), and colors
4. Set primary income category for balance calculations

#### 📊 Viewing Reports & Statistics
Click "📊 Статистика" from main menu:
- **💰 Баланс**: All-time balance (income - expenses) by category
- **📅 Недельный отчет**: Weekly summary
- **📅 Месячный отчет**: Monthly income/expense/net
- **📅 Годовой отчет**: Annual overview
- **📋 Разбивка по категориям**: Detailed category breakdown

## 🏗️ Project Structure

```
telegram_expense_bot/
├── src/
│   ├── bot/
│   │   ├── __init__.py
│   │   └── bot.py              # Main bot logic
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py       # Database connection
│   │   ├── session.py          # Session management
│   │   └── init_db.py          # Database initialization
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── base.py             # Base handler class
│   │   ├── user.py             # User management
│   │   ├── category.py         # Category management
│   │   ├── transaction.py      # Transaction handling
│   │   └── report.py           # Reporting and analytics
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User model
│   │   ├── category.py         # Category model
│   │   └── transaction.py      # Transaction model
│   └── utils/
│       ├── __init__.py
│       └── helpers.py          # Utility functions
├── config/
│   └── settings.py             # Configuration management
├── main.py                     # Application entry point
├── setup_database.py           # Database setup script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 🗄️ Database Schema

### Users Table
- `id`: Primary key
- `telegram_id`: Unique Telegram user ID
- `username`: Telegram username
- `first_name`, `last_name`: User names
- `language_code`: User's language preference
- `is_active`: Account status
- `created_at`, `updated_at`: Timestamps

### Categories Table
- `id`: Primary key
- `name`: Category name
- `description`: Optional description
- `category_type`: Income or Expense
- `color`: Hex color for UI
- `icon`: Emoji or icon identifier
- `is_default`: System default category flag
- `is_active`: Category status
- `user_id`: Foreign key to users
- `created_at`, `updated_at`: Timestamps

### Transactions Table
- `id`: Primary key
- `amount`: Transaction amount
- `description`: Optional description
- `transaction_date`: When transaction occurred
- `user_id`: Foreign key to users
- `category_id`: Foreign key to categories
- `created_at`, `updated_at`: Timestamps

## 🔧 Configuration

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: Your bot token from BotFather
- `DATABASE_URL`: Complete PostgreSQL connection string
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Individual DB settings
- `DEBUG`: Enable debug mode (True/False)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Default Categories
The bot automatically creates these default categories for new users:

**Income Categories:**
- 💰 Salary
- 💼 Freelance
- 📈 Investment
- 💵 Other Income

**Expense Categories:**
- 🍽️ Food & Dining
- 🚗 Transportation
- 🛍️ Shopping
- 🎬 Entertainment
- ⚡ Bills & Utilities
- 🏥 Healthcare
- 📚 Education
- 📝 Other Expenses

## 🚀 Useful Docker Commands

### View Logs
```bash
# Follow bot logs in real-time
docker compose logs -f bot

# View last 50 lines
docker compose logs bot --tail=50

# View database logs
docker compose logs postgres
```

### Manage Services
```bash
# Restart bot only
docker compose restart bot

# Rebuild and restart after code changes
docker compose build bot && docker compose up -d

# Stop all services
docker compose down

# Stop and remove all data (⚠️ deletes database!)
docker compose down -v
```

### Database Access
```bash
# Access PostgreSQL console
docker compose exec postgres psql -U expense_user -d expense_tracker

# Run migrations manually
docker compose exec -T bot python migrations.py

# Backup database
docker compose exec postgres pg_dump -U expense_user expense_tracker > backup.sql

# Restore database
cat backup.sql | docker compose exec -T postgres psql -U expense_user -d expense_tracker
```

### Troubleshooting
```bash
# Check container status
docker compose ps

# Check bot container health
docker compose exec bot python -c "print('Bot container is healthy')"

# Restart from scratch (⚠️ deletes all data!)
docker compose down -v
docker compose build --no-cache
./docker-start.sh
```

## 🎤 Voice Transaction Setup

Voice input uses Google Cloud Speech-to-Text for automatic expense recognition.

### Features
- **Auto-detect** category from speech ("здоровье", "еда", "транспорт")
- **Extract** amount including thousands ("256 тысяч" → 256,000)
- **Recognize** date keywords ("сегодня", "вчера", or defaults to today)
- **Multi-language** support: Russian, English, Ukrainian
- **Instant** transaction creation when all fields recognized

### Setup Steps
1. Create Google Cloud project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable **Cloud Speech-to-Text API**
3. Create service account with Speech-to-Text permissions
4. Download credentials as `credentials.json`
5. Place file in project root: `money_bot/credentials.json`
6. Configure `.env`:
```env
ENABLE_VOICE_INPUT=True
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
SPEECH_RECOGNITION_LANGUAGES=ru-RU,en-US,uk-UA
SPEECH_TARGET_LANGUAGE=ru-RU
```
7. Restart: `docker compose restart bot`

### Disabling Voice Input
Set `ENABLE_VOICE_INPUT=False` in `.env` and restart. The bot will ignore voice messages.

### Using Docker (Production)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Using systemd (Linux)
Create `/etc/systemd/system/expense-bot.service`:
```ini
[Unit]
Description=Expense Tracker Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/money_bot
ExecStart=/usr/bin/python3 main.py
Restart=always
Environment=PYTHONPATH=/path/to/telegram_expense_bot/src

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable expense-bot
sudo systemctl start expense-bot
```

## 🔒 Security Considerations

- Store sensitive data (tokens, passwords) in environment variables
- Use strong database passwords
- Regularly update dependencies
- Monitor bot usage and logs
- Implement rate limiting for production use
- Consider using a reverse proxy for additional security

## 🐛 Troubleshooting

### Common Issues

**Bot not responding:**
- Check if `TELEGRAM_BOT_TOKEN` is correct
- Verify bot is not blocked by users
- Check logs for error messages

**Database connection errors:**
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists and user has permissions

**Import errors:**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python path configuration

### Logs
The bot logs important events and errors. Check the console output or log files for debugging information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Database ORM by [SQLAlchemy](https://www.sqlalchemy.org/)
- PostgreSQL for reliable data storage

## 📞 Support

For support, please open an issue on GitHub or contact the maintainers.

---

**Happy expense tracking! 💰📊**
