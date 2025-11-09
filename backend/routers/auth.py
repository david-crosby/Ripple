"""
Authentication routes.

This module contains all authentication-related endpoints:
- User registration
- User login
- Get current user info
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import get_db
from models import User, GiverProfile, ProfileType
from schemas import UserCreate, UserResponse, Token
from auth import (
    hash_password,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_user_by_username,
    get_user_by_email,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Optional: Import logger if you've created the utils module
# from utils.logger import get_logger
# logger = get_logger(__name__)

# Create router with prefix and tags for organisation
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")  # Limit to 5 registrations per hour per IP
def register_user(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Creates a new user account with the provided information.
    Passwords are automatically hashed before storing.
    Rate limited to 5 registrations per hour per IP address.

    Args:
        request: FastAPI request object (for rate limiting)
        user_data: User registration data (email, username, password, etc.)
        db: Database session (injected)

    Returns:
        Newly created user data (without password)

    Raises:
        HTTPException 400: If username or email already exists
        HTTPException 429: If rate limit exceeded

    Example request body:
        {
            "email": "user@example.com",
            "username": "johndoe",
            "password": "SecurePass123",
            "full_name": "John Doe"
        }
    """
    # Check if username already exists
    existing_user = get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        is_verified=False  # Could implement email verification later
    )
    
    # Add user to database and flush to get the ID
    db.add(new_user)
    db.flush()  # Flush to get the user ID without committing
    
    # Automatically create a giver profile for the new user
    giver_profile = GiverProfile(
        user_id=new_user.id,
        profile_type=ProfileType.INDIVIDUAL,  # Default to individual
        is_public=True
    )
    db.add(giver_profile)
    
    # Commit both user and profile together
    db.commit()
    db.refresh(new_user)  # Refresh to get the auto-generated fields
    
    return new_user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")  # Limit to 10 login attempts per minute per IP
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    User login endpoint.

    Authenticates a user and returns a JWT access token.
    Uses OAuth2PasswordRequestForm which expects form data (not JSON).
    Rate limited to 10 login attempts per minute per IP address.

    Users can log in with either username or email in the 'username' field.

    Args:
        request: FastAPI request object (for rate limiting)
        form_data: OAuth2 form with username and password
        db: Database session (injected)

    Returns:
        Access token and token type

    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 429: If rate limit exceeded

    Example:
        POST /auth/login
        Content-Type: application/x-www-form-urlencoded

        username=user@example.com&password=securepass123
    """
    # Authenticate the user
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's information.
    
    Returns the profile data of the currently authenticated user.
    
    Args:
        current_user: Current authenticated user (injected)
        
    Returns:
        Current user's profile data
        
    Requires:
        Valid JWT token in Authorization header
        
    Example:
        GET /auth/me
        Authorization: Bearer <token>
    """
    return current_user