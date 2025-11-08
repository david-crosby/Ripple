# Donation Endpoints Guide

Complete guide to using the donation endpoints in Ripple.

## Overview

The donation system allows users to contribute to campaigns and tracks all donation activity. When donations are marked as completed, the system automatically updates campaign and giver statistics.

---

## Donation Flow

```
1. User creates donation (PENDING status)
        ↓
2. Payment processed (via Stripe in future)
        ↓
3. Donation status updated to COMPLETED
        ↓
4. Automatic updates:
   - Campaign current_amount += donation amount
   - Giver total_donated += donation amount
   - Giver donation_count += 1
```

---

## Endpoints

### 1. Create Donation

**POST** `/donations/`

Create a new donation to a campaign. Starts with PENDING status.

**Authentication:** Required 🔒

**Request:**
```json
{
  "campaign_id": 1,
  "amount": 50.00,
  "currency": "GBP",
  "is_anonymous": false,
  "message": "Great cause! Happy to help."
}
```

**Validations:**
- Campaign must exist
- Campaign must be ACTIVE
- User must have a giver profile
- Amount must be > 0

**Response:**
```json
{
  "id": 123,
  "amount": 50.00,
  "currency": "GBP",
  "campaign_id": 1,
  "giver_id": 45,
  "payment_status": "pending",
  "is_anonymous": false,
  "message": "Great cause! Happy to help.",
  "created_at": "2025-11-06T12:00:00Z"
}
```

---

### 2. List Campaign Donations

**GET** `/donations/campaigns/{campaign_id}`

Get all completed donations for a campaign.

**Authentication:** Not required

**Query Parameters:**
- `include_anonymous` (boolean, default: false) - Include anonymous donations
- `page` (integer, default: 1) - Page number
- `page_size` (integer, default: 10, max: 100) - Items per page

**Response:**
```json
{
  "donations": [
    {
      "id": 123,
      "amount": 50.00,
      "currency": "GBP",
      "campaign_id": 1,
      "giver_id": 45,
      "payment_status": "completed",
      "is_anonymous": false,
      "message": "Great cause!",
      "created_at": "2025-11-06T12:00:00Z"
    }
  ],
  "total": 25,
  "total_amount": 1250.00,
  "page": 1,
  "page_size": 10
}
```

**Notes:**
- Only returns COMPLETED donations
- By default, excludes anonymous donations
- Returns public donations only (unless include_anonymous=true)

---

### 3. Get Donation Details

**GET** `/donations/{donation_id}`

Get details of a specific donation.

**Authentication:** Required 🔒

**Authorization:**
- Donor can view their own donations
- Campaign creator can view donations to their campaign

**Response:**
```json
{
  "id": 123,
  "amount": 50.00,
  "currency": "GBP",
  "campaign_id": 1,
  "giver_id": 45,
  "payment_status": "completed",
  "payment_intent_id": "pi_1234567890",
  "is_anonymous": false,
  "message": "Great cause!",
  "created_at": "2025-11-06T12:00:00Z",
  "updated_at": "2025-11-06T12:05:00Z"
}
```

---

### 4. Update Donation Status

**PATCH** `/donations/{donation_id}/status`

Update the payment status of a donation.

**Authentication:** Required 🔒

**Authorization:** Only the donor can update their donation

**Query Parameters:**
- `payment_status` (required) - New status: pending, completed, failed, refunded
- `payment_intent_id` (optional) - Stripe payment intent ID

**Example:**
```bash
PATCH /donations/123/status?payment_status=completed&payment_intent_id=pi_test_123
```

**Response:**
```json
{
  "id": 123,
  "amount": 50.00,
  "payment_status": "completed",
  "payment_intent_id": "pi_test_123",
  ...
}
```

**Automatic Updates When Status → COMPLETED:**
1. Campaign `current_amount` increased by donation amount
2. Giver Profile `total_donated` increased by donation amount
3. Giver Profile `donation_count` incremented by 1

---

### 5. Get My Donations

**GET** `/donations/my/donations`

Get donation history for the authenticated user.

**Authentication:** Required 🔒

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `page_size` (integer, default: 10, max: 100) - Items per page

**Response:**
```json
{
  "donations": [...],
  "total": 15,
  "total_amount": 750.00,
  "page": 1,
  "page_size": 10
}
```

**Notes:**
- Shows all donations (all statuses)
- Only shows completed donations in total_amount
- Ordered by most recent first

---

## Payment Statuses

### Status Flow

```
PENDING → COMPLETED
    ↓         ↓
  FAILED   REFUNDED
```

### Status Meanings

- **PENDING** - Donation created, payment not yet processed
- **COMPLETED** - Payment successful, funds received
- **FAILED** - Payment attempt failed
- **REFUNDED** - Payment was refunded to donor

---

## Anonymous Donations

When `is_anonymous: true`:

**What's Hidden:**
- Donor identity in public campaign donation lists
- Donor name/profile in campaign views

**What's Visible:**
- Total donation amount (contributes to campaign total)
- Donation message (if provided)
- To campaign creator: Full donation details
- To donor themselves: Full donation details

**Example:**
```json
{
  "campaign_id": 1,
  "amount": 100.00,
  "is_anonymous": true,
  "message": "Keep up the great work!"
}
```

Public view will show:
- Amount: £100.00
- Donor: "Anonymous"
- Message: "Keep up the great work!"

---

## Testing

### Quick Test

```bash
./test_donations.sh
```

This script will:
1. Create a user and campaign
2. Make 2 donations (1 public, 1 anonymous)
3. Mark both as completed
4. Verify campaign and giver updates
5. List donations

### Manual Testing

```bash
# 1. Create donation
curl -X POST "http://localhost:8000/donations/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": 1,
    "amount": 50.00,
    "currency": "GBP",
    "is_anonymous": false,
    "message": "Great cause!"
  }'

# 2. Complete donation
curl -X PATCH "http://localhost:8000/donations/123/status?payment_status=completed" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. List campaign donations
curl "http://localhost:8000/donations/campaigns/1"

# 4. Get my donations
curl "http://localhost:8000/donations/my/donations" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Integration with Stripe

The donation endpoints are designed to work with Stripe:

1. **Create donation** → Get donation ID
2. **Create Stripe Payment Intent** → Get payment_intent_id
3. **User completes payment on Stripe**
4. **Stripe webhook** → Update donation status to completed
5. **Automatic aggregates** → Campaign and giver stats updated

Example Stripe integration (future):
```python
# When creating donation
donation = create_donation(...)

# Create Stripe payment intent
intent = stripe.PaymentIntent.create(
    amount=int(donation.amount * 100),  # Convert to cents
    currency=donation.currency.lower(),
    metadata={'donation_id': donation.id}
)

# Return intent.client_secret to frontend
# Frontend uses Stripe.js to complete payment
# Stripe webhook confirms payment → update donation status
```

---

## Common Scenarios

### Scenario 1: Regular Public Donation

```bash
# 1. Create donation
POST /donations/
{
  "campaign_id": 1,
  "amount": 25.00,
  "currency": "GBP",
  "is_anonymous": false,
  "message": "Love what you're doing!"
}

# 2. Process payment (via Stripe)
# ... payment processing ...

# 3. Mark as completed
PATCH /donations/123/status?payment_status=completed&payment_intent_id=pi_xxx

# Result:
# - Donation visible in campaign list with donor name
# - Campaign current_amount += 25.00
# - Giver total_donated += 25.00
# - Giver donation_count += 1
```

### Scenario 2: Anonymous Donation

```bash
# 1. Create anonymous donation
POST /donations/
{
  "campaign_id": 1,
  "amount": 100.00,
  "is_anonymous": true
}

# 2. Complete donation
PATCH /donations/456/status?payment_status=completed

# Result:
# - Donation shown as "Anonymous" in public lists
# - Still counts toward campaign total
# - Donor can see it in their history
# - Campaign creator can see full details
```

### Scenario 3: Failed Payment

```bash
# 1. Create donation
POST /donations/ {...}

# 2. Payment fails
PATCH /donations/789/status?payment_status=failed

# Result:
# - Donation marked as failed
# - No impact on campaign or giver totals
# - User can retry or create new donation
```

---

## Best Practices

1. **Always create donations as PENDING first**
   - Never create directly as COMPLETED
   - Let payment processing update the status

2. **Handle payment failures gracefully**
   - Mark as FAILED, not delete
   - Allow user to retry

3. **Respect anonymous donations**
   - Don't expose donor identity in public views
   - Campaign creators can see for tax/reporting

4. **Use appropriate page sizes**
   - Default: 10 items
   - Maximum: 100 items
   - Large lists: paginate

5. **Include payment_intent_id**
   - Essential for Stripe reconciliation
   - Helps with refunds and disputes

---

## Error Handling

### Common Errors

**404 Campaign Not Found**
```json
{
  "detail": "Campaign not found"
}
```

**400 Campaign Not Active**
```json
{
  "detail": "Campaign is not accepting donations (status must be ACTIVE)"
}
```

**403 Not Authorized**
```json
{
  "detail": "Not authorized to update this donation"
}
```

**404 Giver Profile Not Found**
```json
{
  "detail": "Giver profile not found"
}
```

---

## Database Impact

### When Donation Completed

**donations table:**
- payment_status: "pending" → "completed"
- payment_intent_id: updated
- updated_at: current timestamp

**campaigns table:**
- current_amount: += donation.amount

**giver_profiles table:**
- total_donated: += donation.amount
- donation_count: += 1

All updates happen in a single database transaction for consistency.