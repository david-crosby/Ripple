"""
Pydantic schemas for request/response validation.

These schemas define the structure of data coming in (requests) 
and going out (responses) of the API endpoints.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from models import CampaignType, CampaignStatus, ProfileType, PaymentStatus


# ==================== USER SCHEMAS ====================

# User registration schema
class UserCreate(BaseModel):
    """
    Schema for user registration.
    
    Used when a new user signs up.
    """
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name")
    
    class Config:
        # Example data for API documentation
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "securepassword123",
                "full_name": "John Doe"
            }
        }


# User login schema
class UserLogin(BaseModel):
    """
    Schema for user login.
    
    Users can log in with either email or username.
    """
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "securepassword123"
            }
        }


# User response schema (public data only)
class UserResponse(BaseModel):
    """
    Schema for user data in responses.
    
    NEVER includes sensitive data like passwords.
    This is what gets sent to the frontend.
    """
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        # Allow reading data from ORM models
        from_attributes = True


# Token response schema
class Token(BaseModel):
    """
    Schema for JWT token response.
    
    Returned when user successfully logs in or registers.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


# Token data schema (what's stored inside the JWT)
class TokenData(BaseModel):
    """
    Schema for data encoded in JWT tokens.
    
    This is internal - decoded from the token.
    """
    username: Optional[str] = None


# User update schema (for future use)
class UserUpdate(BaseModel):
    """
    Schema for updating user information.
    
    All fields are optional - only update what's provided.
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=255)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "full_name": "John Smith"
            }
        }


# ==================== CAMPAIGN SCHEMAS ====================

class CampaignCreate(BaseModel):
    """
    Schema for creating a new campaign.
    
    Used when users create fundraising campaigns, events, or adhoc giving.
    """
    title: str = Field(..., min_length=5, max_length=255, description="Campaign title")
    description: str = Field(..., min_length=20, description="Detailed description")
    campaign_type: CampaignType = Field(
        default=CampaignType.FUNDRAISING,
        description="Type of campaign"
    )
    goal_amount: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Target amount to raise (optional for adhoc giving)"
    )
    currency: str = Field(default="GBP", max_length=3, description="Currency code")
    start_date: Optional[datetime] = Field(None, description="Campaign start date")
    end_date: Optional[datetime] = Field(None, description="Campaign end date")
    image_url: Optional[str] = Field(None, max_length=500, description="Campaign image URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Help Build a Community Centre",
                "description": "We're raising funds to build a new community centre that will serve...",
                "campaign_type": "fundraising",
                "goal_amount": 50000.00,
                "currency": "GBP",
                "end_date": "2025-12-31T23:59:59Z"
            }
        }


class CampaignUpdate(BaseModel):
    """
    Schema for updating an existing campaign.
    
    All fields are optional - only update what's provided.
    """
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=20)
    goal_amount: Optional[Decimal] = Field(None, gt=0)
    status: Optional[CampaignStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    image_url: Optional[str] = Field(None, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated Campaign Title",
                "status": "active"
            }
        }


class CampaignResponse(BaseModel):
    """
    Schema for campaign data in responses.
    
    Includes all campaign details and creator information.
    """
    id: int
    title: str
    description: str
    campaign_type: CampaignType
    goal_amount: Optional[Decimal]
    current_amount: Decimal
    currency: str
    status: CampaignStatus
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    image_url: Optional[str]
    creator_id: int
    created_at: datetime
    updated_at: datetime
    
    # Calculated fields
    @property
    def percentage_funded(self) -> Optional[float]:
        """Calculate percentage of goal reached."""
        if self.goal_amount and self.goal_amount > 0:
            return float((self.current_amount / self.goal_amount) * 100)
        return None
    
    class Config:
        from_attributes = True


class CampaignListResponse(BaseModel):
    """
    Schema for paginated list of campaigns.
    """
    campaigns: List[CampaignResponse]
    total: int
    page: int
    page_size: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "campaigns": [],
                "total": 100,
                "page": 1,
                "page_size": 10
            }
        }


# ==================== GIVER PROFILE SCHEMAS ====================

class GiverProfileCreate(BaseModel):
    """
    Schema for creating a giver profile.
    
    Created automatically on user registration or manually updated.
    """
    profile_type: ProfileType = Field(
        default=ProfileType.INDIVIDUAL,
        description="Individual or company profile"
    )
    company_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Company name (required for company profiles)"
    )
    bio: Optional[str] = Field(None, description="Biography or company description")
    website_url: Optional[str] = Field(None, max_length=500, description="Website URL")
    is_public: bool = Field(
        default=True,
        description="Whether profile is publicly visible"
    )
    
    @field_validator('company_name')
    @classmethod
    def validate_company_name(cls, v, info):
        """Ensure company_name is provided for company profiles."""
        if info.data.get('profile_type') == ProfileType.COMPANY and not v:
            raise ValueError('company_name is required for company profiles')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "profile_type": "individual",
                "bio": "Passionate about supporting local communities",
                "is_public": True
            }
        }


class GiverProfileUpdate(BaseModel):
    """
    Schema for updating a giver profile.
    
    All fields are optional.
    """
    company_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    website_url: Optional[str] = Field(None, max_length=500)
    is_public: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "bio": "Updated biography",
                "website_url": "https://example.com"
            }
        }


class GiverProfileResponse(BaseModel):
    """
    Schema for giver profile data in responses.
    
    Includes giving statistics and profile information.
    """
    id: int
    user_id: int
    profile_type: ProfileType
    company_name: Optional[str]
    bio: Optional[str]
    website_url: Optional[str]
    total_donated: Decimal
    donation_count: int
    is_public: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== DONATION SCHEMAS ====================

class DonationCreate(BaseModel):
    """
    Schema for creating a donation.
    
    Used when a donor makes a contribution to a campaign.
    """
    campaign_id: int = Field(..., description="Campaign to donate to")
    amount: Decimal = Field(..., gt=0, description="Donation amount")
    currency: str = Field(default="GBP", max_length=3, description="Currency code")
    is_anonymous: bool = Field(
        default=False,
        description="Hide donor identity publicly"
    )
    message: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional message from donor"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": 1,
                "amount": 50.00,
                "currency": "GBP",
                "is_anonymous": False,
                "message": "Great cause! Happy to support."
            }
        }


class DonationResponse(BaseModel):
    """
    Schema for donation data in responses.
    
    Shows donation details with donor information (if not anonymous).
    """
    id: int
    amount: Decimal
    currency: str
    campaign_id: int
    giver_id: int
    payment_status: PaymentStatus
    is_anonymous: bool
    message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DonationListResponse(BaseModel):
    """
    Schema for paginated list of donations.
    """
    donations: List[DonationResponse]
    total: int
    total_amount: Decimal
    page: int
    page_size: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "donations": [],
                "total": 50,
                "total_amount": 2500.00,
                "page": 1,
                "page_size": 10
            }
        }