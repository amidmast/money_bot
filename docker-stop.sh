#!/bin/bash

# Docker Stop Script for Expense Tracker Bot
# This script helps you stop and clean up the bot

set -e

echo "🛑 Stopping Expense Tracker Bot..."

# Stop and remove containers
echo "📦 Stopping containers..."
docker compose down

echo "🧹 Cleaning up..."
# Remove unused images (optional)
read -p "Do you want to remove unused Docker images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker image prune -f
    echo "🗑️  Unused images removed"
fi

# Remove volumes (optional - this will delete all data!)
read -p "Do you want to remove database volumes? This will delete ALL data! (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker compose down -v
    echo "🗑️  Database volumes removed - all data deleted!"
fi

echo "✅ Bot stopped successfully!"
echo ""
echo "📝 To start again, run: ./docker-start.sh"
