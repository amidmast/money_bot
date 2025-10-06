#!/bin/bash

# Expense Tracker Bot Startup Script

echo "🚀 Starting Expense Tracker Bot..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure your settings:"
    echo "cp .env.example .env"
    echo "Then edit .env with your bot token and database settings."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if database is initialized
echo "🗄️ Checking database..."
python setup_database.py

# Start the bot
echo "🤖 Starting the bot..."
python main.py
