from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from src.models.base import Base

# Create database engine
engine = create_engine(settings.database_url, echo=settings.DEBUG)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models is defined in src.models.base and shared across the app

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
