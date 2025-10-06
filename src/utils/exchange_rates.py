"""
Exchange rates management for the Expense Tracker Bot
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings

logger = logging.getLogger(__name__)

# Exchange rates table
Base = declarative_base()

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    
    id = Column(String, primary_key=True)  # Format: "USD_TO_EUR"
    from_currency = Column(String, nullable=False)
    to_currency = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ExchangeRate({self.from_currency}->{self.to_currency}: {self.rate})>"

class ExchangeRateManager:
    def __init__(self):
        self.engine = create_engine(settings.database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Cache for exchange rates
        self._rates_cache: Dict[str, float] = {}
        self._last_update = None
        self._update_interval = timedelta(hours=1)  # Update every hour
        
        # API endpoints
        self.fiat_api_url = "https://api.exchangerate-api.com/v4/latest/USD"
        self.crypto_api_url = "https://api.coingecko.com/api/v3/simple/price"
        
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Get exchange rate between two currencies"""
        if from_currency == to_currency:
            return 1.0
        
        # Check cache first
        cache_key = f"{from_currency}_TO_{to_currency}"
        if cache_key in self._rates_cache:
            return self._rates_cache[cache_key]
        
        # Check database
        db = self.get_session()
        try:
            rate_record = db.query(ExchangeRate).filter(
                ExchangeRate.from_currency == from_currency,
                ExchangeRate.to_currency == to_currency
            ).first()
            
            if rate_record and self._is_rate_fresh(rate_record.last_updated):
                self._rates_cache[cache_key] = rate_record.rate
                return rate_record.rate
        finally:
            db.close()
        
        # Fetch from API
        rate = await self._fetch_exchange_rate(from_currency, to_currency)
        if rate:
            await self._save_exchange_rate(from_currency, to_currency, rate)
            self._rates_cache[cache_key] = rate
            return rate
        
        # Fallback to 1.0 if no rate found
        logger.warning(f"No exchange rate found for {from_currency} to {to_currency}")
        return 1.0
    
    def _is_rate_fresh(self, last_updated: datetime) -> bool:
        """Check if exchange rate is still fresh"""
        if not last_updated:
            return False
        return datetime.utcnow() - last_updated < self._update_interval
    
    async def _fetch_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Fetch exchange rate from API"""
        try:
            # Determine if currencies are fiat or crypto
            from_type = self._get_currency_type(from_currency)
            to_type = self._get_currency_type(to_currency)
            
            if from_type == "fiat" and to_type == "fiat":
                return await self._fetch_fiat_rate(from_currency, to_currency)
            elif from_type == "crypto" or to_type == "crypto":
                return await self._fetch_crypto_rate(from_currency, to_currency)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error fetching exchange rate {from_currency}->{to_currency}: {e}")
            return None
    
    async def _fetch_fiat_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Fetch fiat currency exchange rate"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.fiat_api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        rates = data.get("rates", {})
                        
                        # Convert through USD
                        if from_currency == "USD":
                            return rates.get(to_currency, 1.0)
                        elif to_currency == "USD":
                            from_rate = rates.get(from_currency, 1.0)
                            return 1.0 / from_rate if from_rate != 0 else 1.0
                        else:
                            from_rate = rates.get(from_currency, 1.0)
                            to_rate = rates.get(to_currency, 1.0)
                            return to_rate / from_rate if from_rate != 0 else 1.0
        except Exception as e:
            logger.error(f"Error fetching fiat rate: {e}")
            return None
    
    async def _fetch_crypto_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Fetch cryptocurrency exchange rate"""
        try:
            # Map currency codes to CoinGecko IDs
            crypto_ids = {
                "USDT": "tether",
                "ATOM": "cosmos"
            }
            
            # Get crypto IDs for both currencies
            from_id = crypto_ids.get(from_currency)
            to_id = crypto_ids.get(to_currency)
            
            if not from_id and not to_id:
                # Both are fiat, use fiat API
                return await self._fetch_fiat_rate(from_currency, to_currency)
            
            # Build API request
            ids = []
            if from_id:
                ids.append(from_id)
            if to_id:
                ids.append(to_id)
            
            vs_currencies = []
            if from_currency not in crypto_ids:
                vs_currencies.append(from_currency.lower())
            if to_currency not in crypto_ids:
                vs_currencies.append(to_currency.lower())
            
            if not vs_currencies:
                vs_currencies = ["usd"]  # Default to USD
            
            url = f"{self.crypto_api_url}?ids={','.join(ids)}&vs_currencies={','.join(vs_currencies)}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Parse the response based on currency types
                        if from_currency in crypto_ids and to_currency in crypto_ids:
                            # Crypto to crypto
                            from_price = data.get(from_id, {}).get("usd", 1.0)
                            to_price = data.get(to_id, {}).get("usd", 1.0)
                            return to_price / from_price if from_price != 0 else 1.0
                        
                        elif from_currency in crypto_ids:
                            # Crypto to fiat
                            return data.get(from_id, {}).get(to_currency.lower(), 1.0)
                        
                        elif to_currency in crypto_ids:
                            # Fiat to crypto
                            crypto_price = data.get(to_id, {}).get(from_currency.lower(), 1.0)
                            return 1.0 / crypto_price if crypto_price != 0 else 1.0
                        
        except Exception as e:
            logger.error(f"Error fetching crypto rate: {e}")
            return None
    
    def _get_currency_type(self, currency: str) -> str:
        """Get currency type (fiat or crypto)"""
        from src.utils.translations import SUPPORTED_CURRENCIES
        return SUPPORTED_CURRENCIES.get(currency, {}).get("type", "fiat")
    
    async def _save_exchange_rate(self, from_currency: str, to_currency: str, rate: float):
        """Save exchange rate to database"""
        db = self.get_session()
        try:
            rate_id = f"{from_currency}_TO_{to_currency}"
            
            # Update or create rate record
            rate_record = db.query(ExchangeRate).filter(ExchangeRate.id == rate_id).first()
            if rate_record:
                rate_record.rate = rate
                rate_record.last_updated = datetime.utcnow()
            else:
                rate_record = ExchangeRate(
                    id=rate_id,
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=rate,
                    last_updated=datetime.utcnow()
                )
                db.add(rate_record)
            
            db.commit()
            logger.info(f"Saved exchange rate {from_currency}->{to_currency}: {rate}")
            
        except Exception as e:
            logger.error(f"Error saving exchange rate: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def update_all_rates(self):
        """Update all exchange rates"""
        from src.utils.translations import SUPPORTED_CURRENCIES
        
        currencies = list(SUPPORTED_CURRENCIES.keys())
        logger.info(f"Updating exchange rates for {len(currencies)} currencies")
        
        for from_currency in currencies:
            for to_currency in currencies:
                if from_currency != to_currency:
                    try:
                        rate = await self.get_exchange_rate(from_currency, to_currency)
                        logger.info(f"Updated rate {from_currency}->{to_currency}: {rate}")
                    except Exception as e:
                        logger.error(f"Error updating rate {from_currency}->{to_currency}: {e}")
        
        self._last_update = datetime.utcnow()
        logger.info("Exchange rates update completed")
    
    async def convert_amount(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert amount from one currency to another"""
        if from_currency == to_currency:
            return amount
        
        rate = await self.get_exchange_rate(from_currency, to_currency)
        return amount * rate

# Global instance
exchange_manager = ExchangeRateManager()
