"""
Authentication routes.

This module contains all authentication-related endpoints:
- User registration
- User login
- Get current user info
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models import User, GiverProfile, ProfileType
from schemas import UserCreate, UserResponse, Token
from auth import (
    hash_password,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_user_by_username,
    get_user_by_email
)

# Create router with prefix and tags for organisation
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Creates a new user account with the provided information.
    Passwords are automatically hashed before storing.
    
    Args:
        user_data: User registration data (email, username, password, etc.)
        db: Database session (injected)
        
    Returns:
        Newly created user data (without password)
        
    Raises:
        HTTPException 400: If username or email already exists
        
    Example request body:
        {
            "email": "user@example.com",
            "username": "johndoe",
            "password": "securepassword123",
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
    
    # Add to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh to get the auto-generated fields (id, created_at, etc.)
    
    # Automatically create a giver profile for the new user
    giver_profile = GiverProfile(
        user_id=new_user.id,
        profile_type=ProfileType.INDIVIDUAL,  # Default to individual
        is_public=True
    )
    db.add(giver_profile)
    db.commit()
    
    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    User login endpoint.
    
    Authenticates a user and returns a JWT access token.
    Uses OAuth2PasswordRequestForm which expects form data (not JSON).
    
    Users can log in with either username or email in the 'username' field.
    
    Args:
        form_data: OAuth2 form data with username and password
        db: Database session (injected)
        
    Returns:
        JWT access token and token type
        
    Raises:
        HTTPException 401: If credentials are invalid
        
    Example (using curl):
        curl -X POST "http://localhost:8000/auth/login" \\
             -H "Content-Type: application/x-www-form-urlencoded" \\
             -d "username=johndoe&password=securepassword123"
    """
    # Authenticate user
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    # The "sub" (subject) claim is a standard JWT claim for user identification
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user's information.
    
    This is a protected endpoint that requires authentication.
    Returns the profile of the currently logged-in user.
    
    Args:
        current_user: Current authenticated user (injected from JWT token)
        
    Returns:
        Current user's profile data
        
    Requires:
        Valid JWT token in Authorization header:
        Authorization: Bearer <token>
        
    Example (using curl):
        curl -X GET "http://localhost:8000/auth/me" \\
             -H "Authorization: Bearer YOUR_JWT_TOKEN"
    """
    return current_user


@router.post("/logout")
async def logout():
    """
    Logout endpoint (placeholder).
    
    Note: With JWT tokens, logout is typically handled client-side
    by simply removing the token. The server doesn't need to do anything.
    
    For more advanced logout (token blacklisting), you would need:
    - Redis or similar cache to store invalidated tokens
    - Middleware to check token against blacklist
    
    Returns:
        Success message
    """
    return {
        "message": "Successfully logged out. Please remove the token from your client."
    }