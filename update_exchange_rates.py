#!/usr/bin/env python3
"""
Script to update exchange rates in the database
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.exchange_rates import exchange_manager
from src.database.session import get_session

async def update_exchange_rates():
    """Update exchange rates in the database"""
    print("🔄 Updating exchange rates...")
    
    try:
        # Update exchange rates
        await exchange_manager.update_all_rates()
        print("✅ Exchange rates updated successfully!")
        
        # Show current rates
        with get_session() as session:
            from src.models.exchange_rates import ExchangeRate
            from sqlalchemy import desc
            
            rates = session.query(ExchangeRate).order_by(desc(ExchangeRate.last_updated)).limit(10).all()
            
            if rates:
                print("\n📊 Current exchange rates:")
                for rate in rates:
                    print(f"  {rate.from_currency} → {rate.to_currency}: {rate.rate:.6f}")
            else:
                print("No exchange rates found in database.")
                
    except Exception as e:
        print(f"❌ Error updating exchange rates: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(update_exchange_rates())

