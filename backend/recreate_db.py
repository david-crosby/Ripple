"""
Database Recreation Script
==========================

This script drops all existing tables and recreates them from the current models.py.
Use this when starting fresh or when you want to rebuild the database schema.

WARNING: This will delete ALL data in the database!
"""

from database import Base, engine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def recreate_database():
    """Drop all tables and recreate from current models."""
    
    print("=" * 60)
    print("Database Recreation Script")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print()
    print("Database:", os.getenv("DB_NAME", "fundraiser_dev"))
    print("Host:", os.getenv("DB_HOST", "localhost"))
    print()
    
    response = input("Are you sure you want to continue? (yes/no): ").lower()
    
    if response != 'yes':
        print("❌ Operation cancelled")
        return
    
    print()
    print("🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ All tables dropped")
    
    print()
    print("🔨 Creating tables from models.py...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created")
    
    print()
    print("=" * 60)
    print("✨ Database recreation complete!")
    print("=" * 60)
    print()
    print("Tables created:")
    print("  - users (with profile fields)")
    print("  - campaigns")
    print("  - giver_profiles")
    print("  - donations")
    print()
    print("You can now start your backend with: uvicorn main:app --reload")


if __name__ == "__main__":
    recreate_database()
