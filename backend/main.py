
"""
Main FastAPI application for the fundraiser platform.

This is the entry point for the backend API. It sets up the FastAPI app,
includes routers, and configures middleware.
"""

import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv
import os

# Import database components
from database import engine, get_db, Base, SessionLocal
from models import User

# Import routers
from routers import auth, campaigns, givers, donations, users

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
# This will create all tables defined in models.py if they don't exist
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title=os.getenv("APP_NAME", "Fundraiser Platform API"),
    description="Backend API for the fundraiser platform",
    version="0.1.0",
    docs_url="/docs",  # Swagger UI available at /docs
    redoc_url="/redoc",  # ReDoc available at /redoc
)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows your React frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:5173",  # Vite development server
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Startup event - check database connectivity
@app.on_event("startup")
async def startup_event():
    """
    Check database connectivity on startup.
    
    Ensures the application can connect to the database
    before accepting requests.
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise RuntimeError("Cannot connect to database") from e


# Include routers
app.include_router(auth.router)
app.include_router(campaigns.router)
app.include_router(givers.router)
app.include_router(donations.router)
app.include_router(users.router) 


# Root endpoint
@app.get("/")
def read_root():
    """
    Root endpoint - returns a welcome message.
    
    This is useful for health checks and verifying the API is running.
    """
    return {
        "message": "Welcome to the Fundraiser Platform API",
        "docs": "/docs",
        "version": "0.1.0"
    }


# Health check endpoint
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    
    Verifies that:
    1. The API is running
    2. Database connection is working
    
    Args:
        db: Database session injected by FastAPI's dependency injection
    
    Returns:
        Dictionary with status information
    """
    try:
        # Try to execute a simple query to verify database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


# Example endpoint to test database query
@app.get("/users/count")
def count_users(db: Session = Depends(get_db)):
    """
    Example endpoint showing database interaction.
    
    Returns the total number of users in the database.
    
    Args:
        db: Database session injected by FastAPI's dependency injection
    
    Returns:
        Dictionary with count of users
    """
    count = db.query(User).count()
    return {"count": count}