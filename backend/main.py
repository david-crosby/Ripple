
"""
Main FastAPI application for the fundraiser platform.

This is the entry point for the backend API. It sets up the FastAPI app,
includes routers, and configures middleware.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

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

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


# Lifespan event handler (replaces deprecated on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown events.

    This replaces the deprecated @app.on_event("startup") and @app.on_event("shutdown").
    """
    # Startup: Check database connectivity
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise RuntimeError("Cannot connect to database") from e

    yield

    # Shutdown: Clean up resources (if needed in the future)
    logger.info("Application shutting down")


# Initialize FastAPI application
app = FastAPI(
    title=os.getenv("APP_NAME", "Fundraiser Platform API"),
    description="Backend API for the fundraiser platform",
    version="0.1.0",
    docs_url="/docs",  # Swagger UI available at /docs
    redoc_url="/redoc",  # ReDoc available at /redoc
    lifespan=lifespan,  # Use lifespan handler instead of on_event
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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