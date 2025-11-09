# Ripple API Endpoints Reference

Complete reference of all available API endpoints.

## Base URL
```
http://localhost:8000
```

## Authentication Required
Endpoints marked with 🔒 require a valid JWT token in the Authorization header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Authentication

### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepass123",
  "full_name": "John Doe"
}
```
**Response:** User object (auto-creates giver profile)

### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=securepass123
```
**Response:** JWT access token

### Get Current User 🔒
```http
GET /auth/me
Authorization: Bearer TOKEN
```
**Response:** Current user's profile

### Logout
```http
POST /auth/logout
```
**Response:** Success message (client-side token removal)

---

## User Profile

### Get My Profile 🔒
```http
GET /users/me
Authorization: Bearer TOKEN
```
**Response:** Current user's profile with personal details

### Update My Profile 🔒
```http
PUT /users/me
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+44 7700 900000",
  "address_line1": "123 Main Street",
  "city": "London",
  "postal_code": "SW1A 1AA",
  "country": "United Kingdom"
}
```
**Note:** All fields optional - update only what's provided  
**Response:** Updated user profile

### Get My Statistics 🔒
```http
GET /users/me/stats
Authorization: Bearer TOKEN
```
**Response:** User donation statistics
```json
{
  "total_donated": 500.00,
  "donation_count": 10,
  "has_giver_profile": true
}
```

---

## Campaigns

### Create Campaign 🔒
```http
POST /campaigns/
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "title": "Build a Community Centre",
  "description": "Long description here...",
  "campaign_type": "fundraising",
  "goal_amount": 50000.00,
  "currency": "GBP",
  "end_date": "2025-12-31T23:59:59Z"
}
```
**Campaign Types:** `fundraising`, `event`, `adhoc_giving`  
**Response:** Created campaign (status: DRAFT)

### List Campaigns
```http
GET /campaigns/?campaign_type=fundraising&status=active&page=1&page_size=10
```
**Query Parameters:**
- `campaign_type` - Filter by type (optional)
- `status` - Filter by status (default: active)
- `page` - Page number (default: 1)
- `page_size` - Items per page (max 100, default: 10)

**Response:** Paginated list of campaigns

### Get Campaign
```http
GET /campaigns/{campaign_id}
```
**Response:** Campaign details

### Update Campaign 🔒
```http
PUT /campaigns/{campaign_id}
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "title": "Updated Title",
  "status": "active"
}
```
**Note:** Only creator can update  
**Response:** Updated campaign

### Delete Campaign 🔒
```http
DELETE /campaigns/{campaign_id}
Authorization: Bearer TOKEN
```
**Note:** Only creator can delete (soft delete - sets status to CANCELLED)  
**Response:** 204 No Content

### Get My Campaigns 🔒
```http
GET /campaigns/my/campaigns?page=1&page_size=10
Authorization: Bearer TOKEN
```
**Response:** Paginated list of user's campaigns

---

## Giver Profiles

**Note:** Giver profiles track donation statistics and public giving information, separate from user personal details.

### Get My Giver Profile 🔒
```http
GET /givers/me
Authorization: Bearer TOKEN
```
**Response:** Current user's giver profile with donation statistics

### Get My Giver Profile (Long Form) 🔒
```http
GET /givers/profile/me
Authorization: Bearer TOKEN
```
**Response:** Same as `/givers/me` - alternative endpoint

### Update My Giver Profile 🔒
```http
PUT /givers/profile/me
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "bio": "Updated biography",
  "website_url": "https://newsite.com",
  "is_public": true
}
```
**Note:** Updates bio, website, and privacy settings (not personal details)  
**Response:** Updated giver profile

### Get Public Profile
```http
GET /givers/profile/{user_id}
```
**Note:** Only returns if profile is public  
**Response:** User's public giver profile

### Get My Donations 🔒
```http
GET /givers/me/donations?skip=0&limit=10
Authorization: Bearer TOKEN
```
**Query Parameters:**
- `skip` - Number of items to skip (default: 0)
- `limit` - Items per page (max 100, default: 10)

**Alternative:**
```http
GET /givers/profile/me/donations?page=1&page_size=10
Authorization: Bearer TOKEN
```
**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (max 100, default: 10)

**Response:** Paginated donation history with total amount

### Get Public Donations
```http
GET /givers/profile/{user_id}/donations?page=1&page_size=10
```
**Note:** Only non-anonymous donations from public profiles  
**Response:** Paginated public donations

### Giving Leaderboard
```http
GET /givers/leaderboard?limit=10&profile_type=individual
```
**Query Parameters:**
- `limit` - Number of top givers (max 100, default: 10)
- `profile_type` - Filter by individual/company (optional)

**Response:** Top givers ranked by total donated

---

## Donations

### Create Donation 🔒
```http
POST /donations/
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "campaign_id": 1,
  "amount": 50.00,
  "currency": "GBP",
  "is_anonymous": false,
  "message": "Great cause! Happy to support."
}
```
**Note:** Creates donation with PENDING status  
**Response:** Created donation

### Get Campaign Donations
```http
GET /donations/campaigns/{campaign_id}?include_anonymous=false&page=1&page_size=10
```
**Query Parameters:**
- `include_anonymous` - Include anonymous donations (default: false)
- `page` - Page number (default: 1)
- `page_size` - Items per page (max 100, default: 10)

**Note:** Only returns COMPLETED donations  
**Response:** Paginated donations with total amount

### Get Donation Details 🔒
```http
GET /donations/{donation_id}
Authorization: Bearer TOKEN
```
**Note:** Only donor or campaign creator can view  
**Response:** Donation details

### Update Donation Status 🔒
```http
PATCH /donations/{donation_id}/status?payment_status=completed&payment_intent_id=pi_test_123
Authorization: Bearer TOKEN
```
**Query Parameters:**
- `payment_status` - New status (pending/completed/failed/refunded)
- `payment_intent_id` - Optional Stripe payment intent ID

**Note:** When marked as COMPLETED, automatically updates campaign current_amount and giver statistics  
**Response:** Updated donation

### Get My Donations 🔒
```http
GET /donations/my/donations?page=1&page_size=10
Authorization: Bearer TOKEN
```
**Response:** Paginated donation history with total amount

---

## Health & Info

### Root
```http
GET /
```
**Response:** Welcome message and API info

### Health Check
```http
GET /health
```
**Response:** API and database status

### Protected Endpoint Example 🔒
```http
GET /protected
Authorization: Bearer TOKEN
```
**Response:** Personalised message with user info

---

## Response Formats

### Success Response
```json
{
  "id": 1,
  "title": "Campaign Title",
  "status": "active",
  "created_at": "2025-11-05T10:30:00Z"
}
```

### Error Response
```json
{
  "detail": "Error message here"
}
```

### Paginated Response
```json
{
  "campaigns": [...],
  "total": 100,
  "page": 1,
  "page_size": 10
}
```

---

## Status Codes

- `200` - Success
- `201` - Created
- `204` - No Content (successful deletion)
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (not allowed to perform action)
- `404` - Not Found
- `422` - Validation Error (detailed field errors)

---

## Campaign Status Values

- `draft` - Not yet published
- `active` - Currently accepting donations
- `completed` - Goal reached or ended successfully
- `cancelled` - Cancelled by creator

---

## Payment Status Values

- `pending` - Payment initiated but not confirmed
- `completed` - Payment successful
- `failed` - Payment failed
- `refunded` - Payment refunded

---

## Interactive Documentation

Visit the auto-generated API documentation:

**Swagger UI:** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc

These provide interactive API exploration with try-it-out functionality.

---

## Testing

### Using cURL
```bash
# Get token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=test123" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Use token
curl -X GET "http://localhost:8000/campaigns/my/campaigns" \
  -H "Authorization: Bearer $TOKEN"
```

### Using Test Scripts
```bash
# Test authentication
./test_auth.sh

# Test complete platform
./test_campaigns.sh
```

### Using Swagger UI
1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter: `Bearer YOUR_TOKEN`
4. Test any endpoint interactively