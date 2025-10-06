#!/usr/bin/env python3
"""
Expense Tracker Telegram Bot
Main entry point for the application
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.bot.bot import main

if __name__ == "__main__":
    main()
