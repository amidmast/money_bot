from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    language_code = Column(String, default="en")
    preferred_language = Column(String, default="en")  # User's chosen language
    preferred_currency = Column(String, default="USD")  # User's chosen currency
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    primary_income_category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Group-specific fields
    is_group = Column(Boolean, default=False)
    group_title = Column(String(255))
    group_type = Column(String(50))  # 'group' or 'supergroup'
    
    # Relationships
    categories = relationship(
        "Category",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="Category.user_id"
    )
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        if self.is_group:
            return f"<Group(telegram_id={self.telegram_id}, title={self.group_title})>"
        else:
            return f"<User(telegram_id={self.telegram_id}, username={self.username})>"
