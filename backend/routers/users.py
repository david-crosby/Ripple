"""
User profile routes.

This module contains all user profile-related endpoints:
- View and update user profile information
- Manage personal details and address
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, GiverProfile
from schemas import UserResponse, UserUpdate
from auth import get_current_active_user

# Create router with prefix and tags
router = APIRouter(
    prefix="/users",
    tags=["User Profile"]
)


@router.get("/me", response_model=UserResponse)
def get_my_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's profile information.
    
    Returns the authenticated user's account details including
    personal information and address.
    
    Args:
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Current user's profile
        
    Requires:
        Valid JWT token
        
    Example:
        GET /users/me
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_my_user_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's profile information.
    
    Users can update their personal details, contact information,
    and address. All fields are optional.
    
    Args:
        profile_data: Updated profile data
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Updated user profile
        
    Requires:
        Valid JWT token
        
    Example request:
        {
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+44 7700 900000",
            "address_line1": "123 Main Street",
            "city": "London",
            "postal_code": "SW1A 1AA",
            "country": "United Kingdom"
        }
    """
    # Update fields if provided
    update_data = profile_data.model_dump(exclude_unset=True)
    
    # Check if email is being updated to an existing email
    if 'email' in update_data and update_data['email'] != current_user.email:
        existing_user = db.query(User).filter(
            User.email == update_data['email'],
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    # Apply updates
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/me/stats")
def get_my_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's statistics.
    
    Returns donation statistics and giver profile information.
    
    Args:
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        User statistics including donation totals
        
    Requires:
        Valid JWT token
        
    Example:
        GET /users/me/stats
    """
    # Get giver profile for donation stats
    giver_profile = db.query(GiverProfile).filter(
        GiverProfile.user_id == current_user.id
    ).first()
    
    if not giver_profile:
        return {
            "total_donated": 0.00,
            "donation_count": 0,
            "has_giver_profile": False
        }
    
    return {
        "total_donated": float(giver_profile.total_donated),
        "donation_count": giver_profile.donation_count,
        "has_giver_profile": True
    }