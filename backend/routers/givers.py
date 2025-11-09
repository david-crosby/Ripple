"""
Giver profile routes.

This module contains all giver profile-related endpoints:
- View and update giver profiles
- View donation history
- View giving statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional

from database import get_db
from models import GiverProfile, User, Donation, Campaign, ProfileType, PaymentStatus
from schemas import (
    GiverProfileCreate,
    GiverProfileUpdate,
    GiverProfileResponse,
    DonationListResponse
)
from auth import get_current_active_user

# Create router with prefix and tags
router = APIRouter(
    prefix="/givers",
    tags=["Giver Profiles"]
)


@router.get("/me", response_model=GiverProfileResponse)
def get_my_profile_shorthand(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's giver profile (shorthand endpoint).
    
    Convenience endpoint that returns the authenticated user's giver profile.
    This is the preferred endpoint for getting the current user's profile.
    
    Args:
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Current user's giver profile
        
    Raises:
        HTTPException 404: If profile not found
        
    Requires:
        Valid JWT token
        
    Example:
        GET /givers/me
    """
    profile = db.query(GiverProfile).filter(
        GiverProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Giver profile not found. Create one first."
        )
    
    return profile


@router.post("/profile", response_model=GiverProfileResponse, status_code=status.HTTP_201_CREATED)
def create_giver_profile(
    profile_data: GiverProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a giver profile for the current user.
    
    Each user can have one giver profile. This tracks their donation history
    and preferences.
    
    Args:
        profile_data: Giver profile data
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Newly created giver profile
        
    Raises:
        HTTPException 400: If user already has a profile
        
    Requires:
        Valid JWT token
        
    Example request:
        {
            "profile_type": "individual",
            "bio": "Passionate about supporting local communities",
            "is_public": true
        }
    """
    # Check if user already has a profile
    existing_profile = db.query(GiverProfile).filter(
        GiverProfile.user_id == current_user.id
    ).first()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a giver profile"
        )
    
    # Create new profile
    new_profile = GiverProfile(
        user_id=current_user.id,
        profile_type=profile_data.profile_type,
        company_name=profile_data.company_name,
        bio=profile_data.bio,
        website_url=profile_data.website_url,
        is_public=profile_data.is_public
    )
    
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    
    return new_profile


@router.get("/me/donations", response_model=DonationListResponse)
def get_my_donations_shorthand(
    skip: Optional[int] = Query(None, ge=0, description="Number of items to skip"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Number of items to return"),
    page: Optional[int] = Query(None, ge=1, description="Page number (alternative to skip)"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="Items per page (alternative to limit)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's donation history (shorthand endpoint).
    
    Returns a paginated list of all donations made by the current user.
    Supports both skip/limit and page/page_size parameter styles.
    
    Args:
        skip: Number of items to skip (for offset-based pagination)
        limit: Number of items to return (for offset-based pagination)
        page: Page number (for page-based pagination, starts at 1)
        page_size: Items per page (for page-based pagination)
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Paginated list of donations with total amount
        
    Requires:
        Valid JWT token
        
    Examples:
        GET /givers/me/donations?skip=0&limit=10
        GET /givers/me/donations?page=1&page_size=10
    """
    # Get user's giver profile
    profile = db.query(GiverProfile).filter(
        GiverProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Giver profile not found"
        )
    
    # Handle parameter conversion: support both skip/limit and page/page_size
    if skip is not None or limit is not None:
        # Using skip/limit style
        offset = skip or 0
        items_per_page = limit or 10
        current_page = (offset // items_per_page) + 1
    else:
        # Using page/page_size style (default)
        current_page = page or 1
        items_per_page = page_size or 10
        offset = (current_page - 1) * items_per_page
    
    # Build query for completed donations only
    query = db.query(Donation).filter(
        Donation.giver_id == profile.id,
        Donation.payment_status == PaymentStatus.COMPLETED
    )
    
    # Get total count and amount
    total = query.count()
    total_amount = db.query(func.sum(Donation.amount)).filter(
        Donation.giver_id == profile.id,
        Donation.payment_status == PaymentStatus.COMPLETED
    ).scalar() or 0
    
    # Apply pagination
    donations = query.order_by(desc(Donation.created_at)).offset(offset).limit(items_per_page).all()
    
    return {
        "donations": donations,
        "total": total,
        "total_amount": total_amount,
        "page": current_page,
        "page_size": items_per_page
    }


@router.get("/profile/me", response_model=GiverProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's giver profile.
    
    Returns the authenticated user's giver profile with giving statistics.
    
    Args:
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Current user's giver profile
        
    Raises:
        HTTPException 404: If profile not found
        
    Requires:
        Valid JWT token
        
    Example:
        GET /givers/profile/me
    """
    profile = db.query(GiverProfile).filter(
        GiverProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Giver profile not found. Create one first."
        )
    
    return profile


@router.put("/profile/me", response_model=GiverProfileResponse)
def update_my_profile(
    profile_data: GiverProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's giver profile.
    
    Users can update their biography, website, and privacy settings.
    
    Args:
        profile_data: Updated profile data
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Updated giver profile
        
    Raises:
        HTTPException 404: If profile not found
        
    Requires:
        Valid JWT token
        
    Example request:
        {
            "bio": "Updated biography",
            "website_url": "https://example.com"
        }
    """
    # Get profile
    profile = db.query(GiverProfile).filter(
        GiverProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Giver profile not found. Create one first."
        )
    
    # Update fields if provided
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return profile


@router.get("/profile/{user_id}", response_model=GiverProfileResponse)
def get_profile_by_user_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a public giver profile by user ID.
    
    Only returns profiles that are marked as public.
    
    Args:
        user_id: User ID
        db: Database session (injected)
        
    Returns:
        Public giver profile
        
    Raises:
        HTTPException 404: If profile not found or not public
        
    Example:
        GET /givers/profile/123
    """
    profile = db.query(GiverProfile).filter(
        GiverProfile.user_id == user_id,
        GiverProfile.is_public == True
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public giver profile not found"
        )
    
    return profile


@router.get("/profile/me/donations", response_model=DonationListResponse)
def get_my_donations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's donation history.
    
    Returns a paginated list of all donations made by the current user.
    
    Args:
        page: Page number (starts at 1)
        page_size: Number of items per page (max 100)
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Paginated list of donations with total amount
        
    Requires:
        Valid JWT token
        
    Example:
        GET /givers/profile/me/donations?page=1&page_size=10
    """
    # Get user's giver profile
    profile = db.query(GiverProfile).filter(
        GiverProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Giver profile not found"
        )
    
    # Build query for completed donations only
    query = db.query(Donation).filter(
        Donation.giver_id == profile.id,
        Donation.payment_status == PaymentStatus.COMPLETED
    )
    
    # Get total count and amount
    total = query.count()
    total_amount = db.query(func.sum(Donation.amount)).filter(
        Donation.giver_id == profile.id,
        Donation.payment_status == PaymentStatus.COMPLETED
    ).scalar() or 0
    
    # Apply pagination
    offset = (page - 1) * page_size
    donations = query.order_by(desc(Donation.created_at)).offset(offset).limit(page_size).all()
    
    return {
        "donations": donations,
        "total": total,
        "total_amount": total_amount,
        "page": page,
        "page_size": page_size
    }


@router.get("/profile/{user_id}/donations", response_model=DonationListResponse)
def get_public_donations(
    user_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get public donation history for a user.
    
    Only returns non-anonymous donations for users with public profiles.
    
    Args:
        user_id: User ID
        page: Page number (starts at 1)
        page_size: Number of items per page (max 100)
        db: Database session (injected)
        
    Returns:
        Paginated list of public donations
        
    Raises:
        HTTPException 404: If profile not found or not public
        
    Example:
        GET /givers/profile/123/donations?page=1&page_size=10
    """
    # Get profile and check if public
    profile = db.query(GiverProfile).filter(
        GiverProfile.user_id == user_id,
        GiverProfile.is_public == True
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public giver profile not found"
        )
    
    # Build query for public donations only (non-anonymous, completed)
    query = db.query(Donation).filter(
        Donation.giver_id == profile.id,
        Donation.is_anonymous == False,
        Donation.payment_status == PaymentStatus.COMPLETED
    )
    
    # Get total count and amount
    total = query.count()
    total_amount = db.query(func.sum(Donation.amount)).filter(
        Donation.giver_id == profile.id,
        Donation.is_anonymous == False,
        Donation.payment_status == PaymentStatus.COMPLETED
    ).scalar() or 0
    
    # Apply pagination
    offset = (page - 1) * page_size
    donations = query.order_by(desc(Donation.created_at)).offset(offset).limit(page_size).all()
    
    return {
        "donations": donations,
        "total": total,
        "total_amount": total_amount,
        "page": page,
        "page_size": page_size
    }


@router.get("/leaderboard")
def get_giving_leaderboard(
    limit: int = Query(10, ge=1, le=100, description="Number of top givers"),
    profile_type: Optional[ProfileType] = Query(None, description="Filter by profile type"),
    db: Session = Depends(get_db)
):
    """
    Get the top givers leaderboard.
    
    Returns a list of top donors ranked by total donated amount.
    Only includes users with public profiles.
    
    Args:
        limit: Number of top givers to return (max 100)
        profile_type: Optional filter by individual or company
        db: Database session (injected)
        
    Returns:
        List of top givers with their statistics
        
    Example:
        GET /givers/leaderboard?limit=10&profile_type=individual
    """
    # Build query
    query = db.query(
        GiverProfile,
        User.username,
        User.full_name
    ).join(
        User, GiverProfile.user_id == User.id
    ).filter(
        GiverProfile.is_public == True,
        GiverProfile.total_donated > 0
    )
    
    # Apply profile type filter if provided
    if profile_type:
        query = query.filter(GiverProfile.profile_type == profile_type)
    
    # Order by total donated and limit
    top_givers = query.order_by(desc(GiverProfile.total_donated)).limit(limit).all()
    
    # Format response
    leaderboard = []
    for rank, (profile, username, full_name) in enumerate(top_givers, start=1):
        leaderboard.append({
            "rank": rank,
            "username": username,
            "full_name": full_name,
            "profile_type": profile.profile_type,
            "company_name": profile.company_name,
            "total_donated": float(profile.total_donated),
            "donation_count": profile.donation_count
        })
    
    return {
        "leaderboard": leaderboard,
        "limit": limit
    }