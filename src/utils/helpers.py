"""
Utility functions for the Expense Tracker Bot
"""

from datetime import datetime
from decimal import Decimal
import re

def format_currency(amount, currency="$"):
    """Format amount as currency"""
    if isinstance(amount, (int, float)):
        return f"{currency}{amount:,.2f}"
    elif isinstance(amount, Decimal):
        return f"{currency}{float(amount):,.2f}"
    return f"{currency}0.00"

def format_date(date_obj, format_str="%Y-%m-%d %H:%M"):
    """Format datetime object as string"""
    if isinstance(date_obj, datetime):
        return date_obj.strftime(format_str)
    return str(date_obj)

def validate_amount(amount_str):
    """Validate and convert amount string to float"""
    try:
        # Remove commas and convert to float
        amount = float(amount_str.replace(',', '.'))
        if amount <= 0:
            return None, "Amount must be positive"
        return amount, None
    except ValueError:
        return None, "Invalid amount format"

def validate_category_name(name):
    """Validate category name"""
    if not name or not name.strip():
        return False, "Category name cannot be empty"
    
    name = name.strip()
    if len(name) > 50:
        return False, "Category name too long (max 50 characters)"
    
    # Check for invalid characters
    if not re.match(r'^[a-zA-Z0-9\s\-_&]+$', name):
        return False, "Category name contains invalid characters"
    
    return True, None

def get_month_name(month_num):
    """Get month name from month number"""
    months = ["", "January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    return months[month_num] if 1 <= month_num <= 12 else "Unknown"

def calculate_percentage(part, total):
    """Calculate percentage"""
    if total == 0:
        return 0
    return (part / total) * 100
