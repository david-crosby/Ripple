"""
Database configuration and session management for SQLAlchemy.

This module sets up the database engine, session maker, and base class
for all database models.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
# echo=True will log all SQL statements (useful for development)
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Verify connections before using them
)

# Create a SessionLocal class for database sessions
# Each instance of SessionLocal will be a database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create a Base class for declarative models
# All database models will inherit from this
Base = declarative_base()


def get_db():
    """
    Dependency function to get a database session.
    
    Yields a database session and ensures it's closed after use.
    Use this with FastAPI's Depends() for route dependencies.
    
    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
