# Ripple Data Model

## Entity Relationship Overview

```
┌─────────────┐
│    User     │
│ (Account)   │
└─────┬───────┘
      │
      │ 1:1
      │
      ▼
┌─────────────────┐         ┌──────────────┐
│ GiverProfile    │         │  Campaign    │
│ (Donor Info)    │         │  (Fundraiser)│
└────────┬────────┘         └──────┬───────┘
         │                         │
         │                         │ Creator
         │ 1:N                     │ 1:N
         │                         │
         │    ┌──────────┐        │
         └────►│Donation  │◄───────┘
              │ (Payment) │
              └──────────┘
```

## Models

### User
**Purpose:** Authentication, account management, and user profile

**Key Fields:**
- `id` - Primary key
- `email` - Unique email address
- `username` - Unique username
- `hashed_password` - Bcrypt hashed password
- `full_name` - Full name (legacy field)
- `first_name` - First name
- `last_name` - Last name
- `phone` - Phone number
- `address_line1` - Street address line 1
- `address_line2` - Street address line 2 (optional)
- `city` - City
- `state` - County/State
- `postal_code` - Postal/ZIP code
- `country` - Country
- `is_active` - Account status
- `is_verified` - Email verification status

**Relationships:**
- → Campaign (1:N) - User can create multiple campaigns
- → GiverProfile (1:1) - Each user has one giver profile

---

### Campaign
**Purpose:** Fundraising campaigns, events, and adhoc giving

**Types:**
1. **Fundraising** - Traditional campaigns with goals
2. **Event** - Time-bound event fundraising
3. **Ad-hoc Giving** - Simple one-time giving

**Key Fields:**
- `id` - Primary key
- `title` - Campaign name
- `description` - Full description
- `campaign_type` - Type enum (fundraising/event/adhoc_giving)
- `goal_amount` - Target amount (optional for adhoc)
- `current_amount` - Amount raised so far
- `status` - Campaign status (draft/active/completed/cancelled)
- `start_date` - Launch date (optional)
- `end_date` - Deadline (optional)
- `creator_id` - Foreign key to User

**Relationships:**
- User ← (N:1) - Belongs to one creator
- → Donation (1:N) - Can have multiple donations

**Status Flow:**
```
DRAFT → ACTIVE → COMPLETED
          ↓
      CANCELLED
```

---

### GiverProfile
**Purpose:** Track donor information and giving history

**Profile Types:**
1. **Individual** - Personal donor
2. **Company** - Corporate/business donor

**Key Fields:**
- `id` - Primary key
- `user_id` - Foreign key to User (unique)
- `profile_type` - Individual or company
- `company_name` - Company name (for company profiles)
- `bio` - Biography or description
- `website_url` - Personal or company website
- `total_donated` - Lifetime donation total
- `donation_count` - Number of donations
- `is_public` - Visibility setting

**Relationships:**
- User ← (1:1) - Belongs to one user
- → Donation (1:N) - Can make multiple donations

**Notes:**
- Auto-created on user registration
- Tracks aggregated giving statistics
- Can be public or private

---

### Donation
**Purpose:** Record individual donations to campaigns

**Key Fields:**
- `id` - Primary key
- `amount` - Donation amount
- `currency` - Currency code (default GBP)
- `campaign_id` - Foreign key to Campaign
- `giver_id` - Foreign key to GiverProfile
- `payment_status` - Payment state (pending/completed/failed/refunded)
- `payment_intent_id` - Stripe payment ID
- `is_anonymous` - Hide donor publicly
- `message` - Optional donor message

**Relationships:**
- Campaign ← (N:1) - Belongs to one campaign
- GiverProfile ← (N:1) - Made by one giver

**Payment Status Flow:**
```
PENDING → COMPLETED
    ↓         ↓
  FAILED   REFUNDED
```

---

## Key Relationships

### User Creates Campaigns
- One user can create many campaigns
- Each campaign has one creator
- Creators can update/delete their own campaigns

### User Has One Giver Profile
- Automatically created on registration
- Stores giving statistics and preferences
- Can be individual or company type

### Donations Link Givers and Campaigns
- Many-to-many relationship through donations
- Tracks payment status and amount
- Can be anonymous or public
- Includes optional message

---

## Example Queries

### Get all campaigns by a user
```python
user.campaigns
```

### Get total donated by a user
```python
user.giver_profile.total_donated
```

### Get all donations to a campaign
```python
campaign.donations
```

### Get giver's donation history
```python
giver_profile.donations
```

---

## Aggregations

### Campaign Statistics
- `current_amount` - Sum of all completed donations
- `percentage_funded` - (current_amount / goal_amount) * 100

### Giver Statistics
- `total_donated` - Sum of all completed donations
- `donation_count` - Count of completed donations

These are automatically updated when donations are completed.

---

## Privacy Controls

### Public vs Private Profiles
- `is_public = True` - Profile visible on leaderboards
- `is_public = False` - Profile hidden from public view

### Anonymous Donations
- `is_anonymous = True` - Donor name hidden publicly
- `is_anonymous = False` - Donor name visible

Both settings can be mixed:
- Public profile + anonymous donation
- Private profile + named donation
