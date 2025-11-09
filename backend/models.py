"""
Database models for the fundraiser platform.

This module contains all SQLAlchemy ORM models that represent
database tables.
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, 
    Text, Numeric, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


# Enums for campaign and profile types
class CampaignType(str, enum.Enum):
    """Types of campaigns available on the platform."""
    FUNDRAISING = "fundraising"  # Traditional fundraising with a goal
    EVENT = "event"              # Time-bound event fundraising
    ADHOC_GIVING = "adhoc_giving"  # One-time giving opportunity


class CampaignStatus(str, enum.Enum):
    """Status of a campaign."""
    DRAFT = "draft"          # Not yet published
    ACTIVE = "active"        # Currently accepting donations
    COMPLETED = "completed"  # Goal reached or ended successfully
    CANCELLED = "cancelled"  # Cancelled by creator


class ProfileType(str, enum.Enum):
    """Type of giver profile."""
    INDIVIDUAL = "individual"  # Individual donor
    COMPANY = "company"        # Corporate/business donor


class PaymentStatus(str, enum.Enum):
    """Status of a donation payment."""
    PENDING = "pending"      # Payment initiated but not confirmed
    COMPLETED = "completed"  # Payment successful
    FAILED = "failed"        # Payment failed
    REFUNDED = "refunded"    # Payment refunded


class User(Base):
    """
    User model representing registered users on the platform.
    
    Attributes:
        id: Primary key, auto-incremented
        email: Unique email address for the user
        username: Unique username chosen by the user
        hashed_password: Bcrypt hashed password (never store plain text!)
        full_name: User's full name (legacy field)
        first_name: User's first name
        last_name: User's last name
        phone: Phone number
        address_line1: Street address line 1
        address_line2: Street address line 2 (optional)
        city: City
        state: County/State
        postal_code: Postal/ZIP code
        country: Country
        is_active: Whether the account is active (for soft deletes/suspensions)
        is_verified: Whether the email has been verified
        created_at: Timestamp when the user registered
        updated_at: Timestamp when the user record was last modified
    
    Relationships:
        campaigns: Campaigns created by this user
        giver_profile: The user's giver profile (for tracking donations)
    """
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User credentials and identification
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User information
    full_name = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Address information
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Account status flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps - automatically managed
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="creator")
    giver_profile = relationship("GiverProfile", back_populates="user", uselist=False)
    
    def __repr__(self):
        """String representation of User object for debugging."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Campaign(Base):
    """
    Campaign model representing fundraising campaigns.
    
    Supports three types of campaigns:
    - Fundraising: Traditional campaigns with goals and deadlines
    - Event: Time-bound event fundraising
    - Ad-hoc Giving: Simple one-time giving opportunities
    
    Attributes:
        id: Primary key
        title: Campaign title
        description: Detailed description (supports rich text)
        campaign_type: Type of campaign (fundraising/event/adhoc_giving)
        goal_amount: Target amount to raise (nullable for adhoc)
        current_amount: Current amount raised
        currency: Currency code (default GBP)
        status: Campaign status (draft/active/completed/cancelled)
        start_date: When campaign goes live (nullable)
        end_date: Campaign deadline (nullable)
        image_url: URL to campaign image (S3)
        creator_id: User who created the campaign
        created_at: When campaign was created
        updated_at: When campaign was last modified
    
    Relationships:
        creator: User who created this campaign
        donations: All donations to this campaign
    """
    
    __tablename__ = "campaigns"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Campaign information
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    campaign_type = Column(
        Enum(CampaignType),
        nullable=False,
        default=CampaignType.FUNDRAISING
    )
    
    # Financial information
    goal_amount = Column(
        Numeric(10, 2),
        nullable=True,  # Optional for adhoc giving
        comment="Target amount to raise"
    )
    current_amount = Column(
        Numeric(10, 2),
        default=0.00,
        nullable=False,
        comment="Current amount raised"
    )
    currency = Column(String(3), default="GBP", nullable=False)
    
    # Campaign status and dates
    status = Column(
        Enum(CampaignStatus),
        default=CampaignStatus.DRAFT,
        nullable=False
    )
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Media
    image_url = Column(String(500), nullable=True, comment="S3 image URL")
    
    # Relationships - foreign keys
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    creator = relationship("User", back_populates="campaigns")
    donations = relationship("Donation", back_populates="campaign")
    
    def __repr__(self):
        """String representation of Campaign object for debugging."""
        return f"<Campaign(id={self.id}, title='{self.title}', type='{self.campaign_type}')>"


class GiverProfile(Base):
    """
    Giver profile model for tracking donation history and preferences.
    
    Supports both individual and company profiles. Tracks giving activity
    and stores biographical information.
    
    Attributes:
        id: Primary key
        user_id: Associated user account
        profile_type: Individual or company
        company_name: Company name (if company profile)
        bio: Biography or company description
        website_url: Personal or company website
        total_donated: Lifetime donation total
        donation_count: Total number of donations made
        is_public: Whether profile is publicly visible
        created_at: When profile was created
        updated_at: When profile was last modified
    
    Relationships:
        user: Associated user account
        donations: All donations made by this giver
    """
    
    __tablename__ = "giver_profiles"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Profile information
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )
    profile_type = Column(
        Enum(ProfileType),
        default=ProfileType.INDIVIDUAL,
        nullable=False
    )
    
    # Company-specific fields (nullable for individuals)
    company_name = Column(String(255), nullable=True)
    
    # Biographical information
    bio = Column(Text, nullable=True)
    website_url = Column(String(500), nullable=True)
    
    # Giving statistics
    total_donated = Column(
        Numeric(10, 2),
        default=0.00,
        nullable=False,
        comment="Lifetime total donated"
    )
    donation_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Total number of donations"
    )
    
    # Privacy settings
    is_public = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether profile is publicly visible"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    user = relationship("User", back_populates="giver_profile")
    donations = relationship("Donation", back_populates="giver")
    
    def __repr__(self):
        """String representation of GiverProfile object for debugging."""
        name = self.company_name if self.profile_type == ProfileType.COMPANY else self.user.username
        return f"<GiverProfile(id={self.id}, type='{self.profile_type}', name='{name}')>"


class Donation(Base):
    """
    Donation model representing individual donations to campaigns.
    
    Tracks all donation activity, including payment status, donor information,
    and optional messages of support.
    
    Attributes:
        id: Primary key
        amount: Donation amount
        currency: Currency code
        campaign_id: Campaign receiving the donation
        giver_id: Giver profile making the donation
        payment_status: Status of the payment
        payment_intent_id: Stripe payment intent ID
        is_anonymous: Whether to hide donor identity
        message: Optional message from donor
        created_at: When donation was made
        updated_at: When donation record was last modified
    
    Relationships:
        campaign: Campaign receiving this donation
        giver: Giver profile that made this donation
    """
    
    __tablename__ = "donations"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Financial information
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="GBP", nullable=False)
    
    # Relationships - foreign keys
    campaign_id = Column(
        Integer,
        ForeignKey("campaigns.id"),
        nullable=False,
        index=True
    )
    giver_id = Column(
        Integer,
        ForeignKey("giver_profiles.id"),
        nullable=False,
        index=True
    )
    
    # Payment information
    payment_status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False
    )
    payment_intent_id = Column(
        String(255),
        nullable=True,
        comment="Stripe payment intent ID"
    )
    
    # Donation details
    is_anonymous = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Hide donor identity publicly"
    )
    message = Column(Text, nullable=True, comment="Optional message from donor")
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    campaign = relationship("Campaign", back_populates="donations")
    giver = relationship("GiverProfile", back_populates="donations")
    
    def __repr__(self):
        """String representation of Donation object for debugging."""
        return f"<Donation(id={self.id}, amount={self.amount}, campaign_id={self.campaign_id})>"