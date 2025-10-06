"""
Exchange rates model for storing currency conversion rates
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Index
from sqlalchemy.sql import func
from .base import Base


class ExchangeRate(Base):
    __tablename__ = 'exchange_rates'
    
    id = Column(Integer, primary_key=True)
    from_currency = Column(String(10), nullable=False)
    to_currency = Column(String(10), nullable=False)
    rate = Column(Numeric(20, 8), nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Index for faster lookups
    __table_args__ = (
        Index('idx_exchange_rates_pair', 'from_currency', 'to_currency'),
        Index('idx_exchange_rates_updated', 'last_updated'),
    )
    
    def __repr__(self):
        return f"<ExchangeRate({self.from_currency}->{self.to_currency}: {self.rate})>"

