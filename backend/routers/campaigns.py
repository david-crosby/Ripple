"""
Campaign routes.

This module contains all campaign-related endpoints:
- Create, read, update, delete campaigns
- List campaigns with filters
- Get campaign donations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Campaign, User, CampaignType, CampaignStatus
from schemas import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignListResponse
)
from auth import get_current_active_user

# Create router with prefix and tags
router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"]
)


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new campaign.
    
    Authenticated users can create fundraising campaigns, events, or adhoc giving opportunities.
    Campaigns are created in DRAFT status by default.
    
    Args:
        campaign_data: Campaign creation data
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Newly created campaign
        
    Requires:
        Valid JWT token
        
    Example request:
        {
            "title": "Help Build a Community Centre",
            "description": "We're raising funds for...",
            "campaign_type": "fundraising",
            "goal_amount": 50000.00,
            "end_date": "2025-12-31T23:59:59Z"
        }
    """
    # Create new campaign
    new_campaign = Campaign(
        title=campaign_data.title,
        description=campaign_data.description,
        campaign_type=campaign_data.campaign_type,
        goal_amount=campaign_data.goal_amount,
        currency=campaign_data.currency,
        start_date=campaign_data.start_date,
        end_date=campaign_data.end_date,
        image_url=campaign_data.image_url,
        creator_id=current_user.id,
        status=CampaignStatus.DRAFT  # New campaigns start as drafts
    )
    
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    
    return new_campaign


@router.get("/", response_model=CampaignListResponse)
def list_campaigns(
    campaign_type: Optional[CampaignType] = Query(None, description="Filter by campaign type"),
    status: Optional[CampaignStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List all campaigns with optional filters.
    
    Returns a paginated list of campaigns. Filters can be applied for
    campaign type and status.
    
    Args:
        campaign_type: Optional filter by campaign type
        status: Optional filter by status (defaults to showing ACTIVE campaigns)
        page: Page number (starts at 1)
        page_size: Number of items per page (max 100)
        db: Database session (injected)
        
    Returns:
        Paginated list of campaigns
        
    Example:
        GET /campaigns?campaign_type=fundraising&status=active&page=1&page_size=10
    """
    # Build query
    query = db.query(Campaign)
    
    # Apply filters
    if campaign_type:
        query = query.filter(Campaign.campaign_type == campaign_type)
    
    # Default to showing active campaigns if no status specified
    if status:
        query = query.filter(Campaign.status == status)
    else:
        query = query.filter(Campaign.status == CampaignStatus.ACTIVE)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    campaigns = query.order_by(Campaign.created_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "campaigns": campaigns,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific campaign by ID.
    
    Returns detailed information about a single campaign.
    
    Args:
        campaign_id: Campaign ID
        db: Database session (injected)
        
    Returns:
        Campaign details
        
    Raises:
        HTTPException 404: If campaign not found
        
    Example:
        GET /campaigns/1
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing campaign.
    
    Only the campaign creator can update their campaign.
    
    Args:
        campaign_id: Campaign ID to update
        campaign_data: Updated campaign data
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Updated campaign
        
    Raises:
        HTTPException 404: If campaign not found
        HTTPException 403: If user is not the campaign creator
        
    Requires:
        Valid JWT token
        User must be campaign creator
        
    Example:
        PUT /campaigns/1
        {
            "title": "Updated Title",
            "status": "active"
        }
    """
    # Get campaign
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if user is the creator
    if campaign.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own campaigns"
        )
    
    # Update fields if provided
    update_data = campaign_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    db.commit()
    db.refresh(campaign)
    
    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a campaign.
    
    Only the campaign creator can delete their campaign.
    This is a soft delete - the campaign status is set to CANCELLED.
    
    Args:
        campaign_id: Campaign ID to delete
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        No content (204)
        
    Raises:
        HTTPException 404: If campaign not found
        HTTPException 403: If user is not the campaign creator
        
    Requires:
        Valid JWT token
        User must be campaign creator
        
    Example:
        DELETE /campaigns/1
    """
    # Get campaign
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if user is the creator
    if campaign.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own campaigns"
        )
    
    # Soft delete - set status to cancelled
    campaign.status = CampaignStatus.CANCELLED
    db.commit()
    
    return None


@router.get("/my/campaigns", response_model=CampaignListResponse)
def get_my_campaigns(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all campaigns created by the current user.
    
    Returns a paginated list of the current user's campaigns.
    
    Args:
        page: Page number (starts at 1)
        page_size: Number of items per page (max 100)
        current_user: Current authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Paginated list of user's campaigns
        
    Requires:
        Valid JWT token
        
    Example:
        GET /campaigns/my/campaigns?page=1&page_size=10
    """
    # Get user's campaigns
    query = db.query(Campaign).filter(Campaign.creator_id == current_user.id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    campaigns = query.order_by(Campaign.created_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "campaigns": campaigns,
        "total": total,
        "page": page,
        "page_size": page_size
    }