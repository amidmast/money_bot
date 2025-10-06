from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .base import Base

class CategoryType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String, nullable=False)  # English name
    name_ru = Column(String, nullable=False)  # Russian name
    description_en = Column(String, nullable=True)  # English description
    description_ru = Column(String, nullable=True)  # Russian description
    category_type = Column(Enum(CategoryType), nullable=False)
    color = Column(String, default="#3498db")  # Hex color for UI
    icon = Column(String, nullable=True)  # Emoji or icon identifier
    is_default = Column(Boolean, default=False)  # System default categories
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship(
        "User",
        back_populates="categories",
        foreign_keys="Category.user_id"
    )
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")
    
    def get_name(self, language: str = "en") -> str:
        """Get localized category name"""
        if language == "ru":
            return self.name_ru
        return self.name_en
    
    def get_description(self, language: str = "en") -> str:
        """Get localized category description"""
        if language == "ru":
            return self.description_ru or ""
        return self.description_en or ""
    
    def __repr__(self):
        return f"<Category(name_en={self.name_en}, name_ru={self.name_ru}, type={self.category_type.value})>"
