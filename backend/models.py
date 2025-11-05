"""
Database models for the fundraiser platform.

This module contains all SQLAlchemy ORM models that represent
database tables.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """
    User model representing registered users on the platform.
    
    Attributes:
        id: Primary key, auto-incremented
        email: Unique email address for the user
        username: Unique username chosen by the user
        hashed_password: Bcrypt hashed password (never store plain text!)
        full_name: User's full name
        is_active: Whether the account is active (for soft deletes/suspensions)
        is_verified: Whether the email has been verified
        created_at: Timestamp when the user registered
        updated_at: Timestamp when the user record was last modified
    """
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User credentials and identification
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User information
    full_name = Column(String(255), nullable=True)
    
    # Account status flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps - automatically managed
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self):
        """String representation of User object for debugging."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
