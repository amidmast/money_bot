from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="USD", nullable=False)  # Transaction currency
    description = Column(Text, nullable=True)
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(amount={self.amount}, category={self.category.name if self.category else None})>"
    
    @property
    def is_income(self):
        return self.category and self.category.category_type.value == "income"
    
    @property
    def is_expense(self):
        return self.category and self.category.category_type.value == "expense"
