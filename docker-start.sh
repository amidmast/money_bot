#!/bin/bash

# Docker Start Script for Expense Tracker Bot
# This script helps you start the bot with Docker Compose

set -e

echo "🚀 Starting Expense Tracker Bot with Docker Compose..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📋 Creating .env file from template..."
    cp env.example .env
    echo "✏️  Please edit .env file and add your TELEGRAM_BOT_TOKEN"
    echo "   You can get your bot token from @BotFather on Telegram"
    echo ""
    echo "Press Enter when you're ready to continue..."
    read
fi

# Check if TELEGRAM_BOT_TOKEN is set
if ! grep -q "TELEGRAM_BOT_TOKEN=your_bot_token_here" .env; then
    echo "✅ .env file looks good"
else
    echo "❌ Please set your TELEGRAM_BOT_TOKEN in .env file"
    echo "   Current value: $(grep TELEGRAM_BOT_TOKEN .env)"
    exit 1
fi

# Build and start services
echo "🔨 Building Docker images..."
docker compose build

echo "🚀 Starting services..."
docker compose up -d

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "🗄️  Initializing database (migrations)..."
docker compose exec -T bot python migrations.py

echo "✅ Bot is starting up!"
echo ""
echo "📊 Services status:"
docker compose ps

echo ""
echo "📝 Useful commands:"
echo "  View logs:           docker compose logs -f bot"
echo "  Stop services:       docker compose down"
echo "  Restart bot:         docker compose restart bot"
echo "  Access database:     docker compose exec postgres psql -U expense_user -d expense_tracker"
echo "  View pgAdmin:        http://localhost:8080 (admin@example.com / admin)"
echo ""
echo "🎉 Your bot should be running now! Check the logs above for any errors."
