# 💰 Expense Tracker Telegram Bot

A comprehensive Telegram bot for tracking income and expenses with PostgreSQL backend, featuring category management, detailed reporting, and analytics.

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
- **📊 Visual Reports**: Monthly and yearly expense breakdowns
- **⚡ Real-time Updates**: Instant balance and transaction updates
- **🌍 Supported Currencies**: USD, USDT, ATOM, UAH
- **🔄 Exchange Rate Updates**: Automatic hourly updates from multiple APIs
- **💱 Currency Conversion**: Real-time conversion between all supported currencies

### User Experience
- **🤖 Intuitive Interface**: Easy-to-use inline keyboard navigation
- **📱 Mobile Optimized**: Perfect for mobile Telegram usage
- **🔄 Quick Actions**: Fast transaction entry and category management
- **💾 Persistent Storage**: All data securely stored in PostgreSQL
- **🔒 User Isolation**: Each user's data is completely separate
- **🌐 Language Selection**: Choose your preferred language (English/Russian)
- **💱 Currency Selection**: Select currency for each transaction
- **📊 Unified Balance**: View all balances converted to your preferred currency

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 12 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### 1. Clone the Repository
```bash
git clone <repository-url>
cd telegram_expense_bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
Create a PostgreSQL database:
```sql
CREATE DATABASE expense_tracker;
CREATE USER expense_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE expense_tracker TO expense_user;
```

### 4. Environment Configuration
Copy the example environment file and configure it:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Database Configuration
DATABASE_URL=postgresql://expense_user:your_password@localhost:5432/expense_tracker

# Optional: Individual database settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=expense_tracker
DB_USER=expense_user
DB_PASSWORD=your_password

# Application Configuration
DEBUG=True
LOG_LEVEL=INFO
```

### 5. Initialize Database
```bash
python setup_database.py
```

### 6. Run the Bot
```bash
python main.py
```

## 📱 Usage

### Getting Started
1. Start a conversation with your bot on Telegram
2. Send `/start` to initialize your account
3. The bot will create default categories for you
4. Use the inline keyboard to navigate through features

### Commands
- `/start` - Initialize bot and show main menu
- `/help` - Display help information
- `/balance` - Show current financial summary

### Main Features

#### 💰 Adding Transactions
1. Click "Add Transaction" from main menu
2. Choose "Add Income" or "Add Expense"
3. Select a category from the list
4. Enter the amount
5. Transaction is automatically saved

#### 🏷️ Managing Categories
1. Click "Manage Categories" from main menu
2. Choose to add, view, edit, or delete categories
3. Create custom categories with icons and descriptions
4. Organize your finances exactly how you want

#### 📊 Viewing Reports
1. Click "View Reports" from main menu
2. Choose from:
   - **Monthly Report**: Current month's income, expenses, and balance
   - **Yearly Report**: Annual summary with monthly breakdown
   - **Category Breakdown**: Detailed spending by category
   - **Analytics**: Usage statistics and insights

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

## 🚀 Deployment

### Using Docker Compose (Recommended for Testing)

The easiest way to run the bot for testing is using Docker Compose. This will set up both the bot and PostgreSQL database automatically.

#### Quick Start

1. **Get your Telegram Bot Token:**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Create a new bot with `/newbot`
   - Copy the bot token

2. **Set up environment:**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env and add your bot token
   nano .env
   ```

3. **Start the bot:**
   ```bash
   # Make scripts executable (if needed)
   chmod +x docker-start.sh docker-stop.sh
   
   # Start the bot
   ./docker-start.sh
   ```

4. **Stop the bot:**
   ```bash
   ./docker-stop.sh
   ```

#### Manual Docker Commands

If you prefer to use Docker commands directly:

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f bot

# Stop services
docker-compose down

# Stop and remove all data
docker-compose down -v
```

#### Services Included

- **Bot**: The Telegram bot application
- **PostgreSQL**: Database for storing user data
- **pgAdmin**: Web interface for database management
  - Access at: http://localhost:8080
  - Login: admin@example.com / admin

#### Environment Variables

The Docker setup uses these default values:
- Database: `expense_tracker`
- User: `expense_user`
- Password: `expense_password`
- Port: `5432`

You can modify these in `docker-compose.yml` or override them in your `.env` file.

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
WorkingDirectory=/path/to/telegram_expense_bot
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
