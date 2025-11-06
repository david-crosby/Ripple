"""
Donation routes.

This module contains all donation-related endpoints:
- Create donations
- List campaign donations
- Update donation status
- Process donation completion
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from decimal import Decimal

from database import get_db
from models import (
    Donation, Campaign, GiverProfile, User,
    PaymentStatus, CampaignStatus
)
from schemas import DonationCreate, DonationResponse, DonationListResponse
from auth import get_current_active_user

# Create router with prefix and tags
router = APIRouter(
    prefix="/donations",
    tags=["Donations"]
)


@router.post("/", response_model=DonationResponse, status_code=status.HTTP_201_CREATED)
def create_donation(
    donation_data: DonationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new donation.
    
    Creates a donation with PENDING status. Once payment is processed,
    use the update endpoint to mark as COMPLETED.
    
    Args:
        donation_data: Donation creation data
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Newly created donation
        
    Raises:
        HTTPException 404: If campaign or giver profile not found
        HTTPException 400: If campaign is not active
        
    Requires:
        Valid JWT token
        User must have a giver profile
        
    Example request:
        {
            "campaign_id": 1,
            "amount": 50.00,
            "currency": "GBP",
            "is_anonymous": false,
            "message": "Great cause! Happy to support."
        }
    """
    # Get the campaign
    campaign = db.query(Campaign).filter(Campaign.id == donation_data.campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if campaign is active
    if campaign.status != CampaignStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign is not accepting donations (status must be ACTIVE)"
        )
    
    # Get user's giver profile
    giver_profile = db.query(GiverProfile).filter(
        GiverProfile.user_id == current_user.id
    ).first()
    
    if not giver_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Giver profile not found. This should have been auto-created."
        )
    
    # Create the donation with PENDING status
    new_donation = Donation(
        amount=donation_data.amount,
        currency=donation_data.currency,
        campaign_id=donation_data.campaign_id,
        giver_id=giver_profile.id,
        payment_status=PaymentStatus.PENDING,
        is_anonymous=donation_data.is_anonymous,
        message=donation_data.message
    )
    
    db.add(new_donation)
    db.commit()
    db.refresh(new_donation)
    
    return new_donation


@router.get("/campaigns/{campaign_id}", response_model=DonationListResponse)
def get_campaign_donations(
    campaign_id: int,
    include_anonymous: bool = Query(False, description="Include anonymous donations"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get all donations for a specific campaign.
    
    Returns completed donations for a campaign. By default, respects
    anonymous donation settings.
    
    Args:
        campaign_id: Campaign ID
        include_anonymous: Whether to include anonymous donations (default: False)
        page: Page number (starts at 1)
        page_size: Number of items per page (max 100)
        db: Database session (injected)
        
    Returns:
        Paginated list of donations with total amount
        
    Raises:
        HTTPException 404: If campaign not found
        
    Example:
        GET /donations/campaigns/1?page=1&page_size=10
    """
    # Check if campaign exists
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Build query for completed donations
    query = db.query(Donation).filter(
        Donation.campaign_id == campaign_id,
        Donation.payment_status == PaymentStatus.COMPLETED
    )
    
    # Filter out anonymous donations if not requested
    if not include_anonymous:
        query = query.filter(Donation.is_anonymous == False)
    
    # Get total count and amount
    total = query.count()
    
    total_amount = db.query(Donation.amount).filter(
        Donation.campaign_id == campaign_id,
        Donation.payment_status == PaymentStatus.COMPLETED
    ).all()
    total_amount = sum(float(amount[0]) for amount in total_amount) if total_amount else 0
    
    # Apply pagination
    offset = (page - 1) * page_size
    donations = query.order_by(desc(Donation.created_at)).offset(offset).limit(page_size).all()
    
    return {
        "donations": donations,
        "total": total,
        "total_amount": Decimal(str(total_amount)),
        "page": page,
        "page_size": page_size
    }


@router.get("/{donation_id}", response_model=DonationResponse)
def get_donation(
    donation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific donation by ID.
    
    Only the donor or campaign creator can view the donation details.
    
    Args:
        donation_id: Donation ID
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Donation details
        
    Raises:
        HTTPException 404: If donation not found
        HTTPException 403: If user is not authorized to view
        
    Requires:
        Valid JWT token
        
    Example:
        GET /donations/123
    """
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    
    if not donation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donation not found"
        )
    
    # Check authorization - donor, campaign creator, or admin
    giver_profile = db.query(GiverProfile).filter(
        GiverProfile.user_id == current_user.id
    ).first()
    
    campaign = db.query(Campaign).filter(Campaign.id == donation.campaign_id).first()
    
    is_donor = giver_profile and giver_profile.id == donation.giver_id
    is_creator = campaign and campaign.creator_id == current_user.id
    
    if not (is_donor or is_creator):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this donation"
        )
    
    return donation


@router.patch("/{donation_id}/status", response_model=DonationResponse)
def update_donation_status(
    donation_id: int,
    payment_status: PaymentStatus,
    payment_intent_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update donation payment status.
    
    When a donation is marked as COMPLETED, automatically updates:
    - Campaign current_amount
    - Giver profile total_donated and donation_count
    
    Args:
        donation_id: Donation ID
        payment_status: New payment status
        payment_intent_id: Optional Stripe payment intent ID
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Updated donation
        
    Raises:
        HTTPException 404: If donation not found
        HTTPException 403: If user is not authorized
        
    Requires:
        Valid JWT token
        User must be the donor
        
    Example:
        PATCH /donations/123/status?payment_status=completed
    """
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    
    if not donation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donation not found"
        )
    
    # Check authorization - only the donor can update their donation
    giver_profile = db.query(GiverProfile).filter(
        GiverProfile.user_id == current_user.id
    ).first()
    
    if not giver_profile or giver_profile.id != donation.giver_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this donation"
        )
    
    # Store old status to check if it's changing to COMPLETED
    old_status = donation.payment_status
    
    # Update donation status
    donation.payment_status = payment_status
    
    if payment_intent_id:
        donation.payment_intent_id = payment_intent_id
    
    # If donation just became COMPLETED, update aggregates
    if old_status != PaymentStatus.COMPLETED and payment_status == PaymentStatus.COMPLETED:
        _update_donation_aggregates(db, donation)
    
    db.commit()
    db.refresh(donation)
    
    return donation


def _update_donation_aggregates(db: Session, donation: Donation):
    """
    Update campaign and giver profile aggregates when donation is completed.
    
    Internal helper function called when a donation status changes to COMPLETED.
    
    Args:
        db: Database session
        donation: The completed donation
    """
    # Update campaign current_amount
    campaign = db.query(Campaign).filter(Campaign.id == donation.campaign_id).first()
    if campaign:
        campaign.current_amount += donation.amount
    
    # Update giver profile statistics
    giver_profile = db.query(GiverProfile).filter(GiverProfile.id == donation.giver_id).first()
    if giver_profile:
        giver_profile.total_donated += donation.amount
        giver_profile.donation_count += 1


@router.get("/my/donations", response_model=DonationListResponse)
def get_my_donations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all donations made by the current user.
    
    Returns the authenticated user's complete donation history.
    
    Args:
        page: Page number (starts at 1)
        page_size: Number of items per page (max 100)
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Paginated list of user's donations with total amount
        
    Raises:
        HTTPException 404: If giver profile not found
        
    Requires:
        Valid JWT token
        
    Example:
        GET /donations/my/donations?page=1&page_size=10
    """
    # Get user's giver profile
    giver_profile = db.query(GiverProfile).filter(
        GiverProfile.user_id == current_user.id
    ).first()
    
    if not giver_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Giver profile not found"
        )
    
    # Build query
    query = db.query(Donation).filter(Donation.giver_id == giver_profile.id)
    
    # Get total count and amount (all statuses)
    total = query.count()
    
    total_amount = db.query(Donation.amount).filter(
        Donation.giver_id == giver_profile.id,
        Donation.payment_status == PaymentStatus.COMPLETED
    ).all()
    total_amount = sum(float(amount[0]) for amount in total_amount) if total_amount else 0
    
    # Apply pagination
    offset = (page - 1) * page_size
    donations = query.order_by(desc(Donation.created_at)).offset(offset).limit(page_size).all()
    
    return {
        "donations": donations,
        "total": total,
        "total_amount": Decimal(str(total_amount)),
        "page": page,
        "page_size": page_size
    }