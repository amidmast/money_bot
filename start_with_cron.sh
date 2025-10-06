#!/bin/bash

# Start cron daemon in background
cron

# Add cron job to update exchange rates every hour
echo "0 * * * * cd /app && python update_exchange_rates.py >> /var/log/exchange_rates.log 2>&1" | crontab -

# Start the main application
exec python main.py
