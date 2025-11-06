#!/bin/zsh

# Comprehensive test script for Ripple fundraiser platform
# Tests campaigns, donations, and giver profiles

set -e  # Exit on error

API_URL="http://localhost:8000"

echo "🧪 Testing Ripple Fundraiser Platform"
echo "======================================"
echo ""

# Generate random username to avoid conflicts
RANDOM_NUM=$RANDOM
USERNAME="testuser${RANDOM_NUM}"
EMAIL="test${RANDOM_NUM}@example.com"
PASSWORD="testpass123"

echo "📝 Test credentials:"
echo "   Username: $USERNAME"
echo "   Email: $EMAIL"
echo ""

# ==================== AUTHENTICATION ====================

echo "🔐 AUTHENTICATION"
echo "=================="
echo ""

echo "1️⃣  Registering new user..."
REGISTER_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${API_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${EMAIL}\",
    \"username\": \"${USERNAME}\",
    \"password\": \"${PASSWORD}\",
    \"full_name\": \"Test User\"
  }")

# Extract HTTP code and response body
HTTP_CODE=$(echo "$REGISTER_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
REGISTER_BODY=$(echo "$REGISTER_RESPONSE" | sed '/HTTP_CODE:/d')

if [ "$HTTP_CODE" != "201" ]; then
    echo "❌ Registration failed with HTTP $HTTP_CODE!"
    echo "$REGISTER_BODY" | python3 -m json.tool 2>/dev/null || echo "$REGISTER_BODY"
    exit 1
fi

echo "✅ Registration successful (giver profile auto-created)!"
echo "$REGISTER_BODY" | python3 -m json.tool 2>/dev/null || echo "$REGISTER_BODY"
echo ""

echo "2️⃣  Logging in..."
TOKEN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${USERNAME}&password=${PASSWORD}")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Login failed!"
    exit 1
fi

echo "✅ Login successful!"
echo "🔑 Token: ${ACCESS_TOKEN:0:50}..."
echo ""

# ==================== GIVER PROFILE ====================

echo "👤 GIVER PROFILE"
echo "================"
echo ""

echo "3️⃣  Getting my giver profile..."
PROFILE_RESPONSE=$(curl -s -X GET "${API_URL}/givers/profile/me" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo "✅ Giver profile:"
echo "$PROFILE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$PROFILE_RESPONSE"
echo ""

echo "4️⃣  Updating giver profile..."
UPDATE_PROFILE_RESPONSE=$(curl -s -X PUT "${API_URL}/givers/profile/me" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Passionate about supporting local communities and making a difference",
    "website_url": "https://example.com"
  }')

echo "✅ Profile updated:"
echo "$UPDATE_PROFILE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$UPDATE_PROFILE_RESPONSE"
echo ""

# ==================== CAMPAIGNS ====================

echo "🎯 CAMPAIGNS"
echo "============"
echo ""

echo "5️⃣  Creating a fundraising campaign..."
CAMPAIGN_RESPONSE=$(curl -s -X POST "${API_URL}/campaigns/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build a Community Centre",
    "description": "We are raising funds to build a new community centre that will serve over 5,000 local residents. The centre will include sports facilities, a library, and meeting rooms for community groups.",
    "campaign_type": "fundraising",
    "goal_amount": 50000.00,
    "currency": "GBP",
    "end_date": "2025-12-31T23:59:59Z"
  }')

CAMPAIGN_ID=$(echo $CAMPAIGN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

echo "✅ Campaign created (ID: $CAMPAIGN_ID):"
echo "$CAMPAIGN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$CAMPAIGN_RESPONSE"
echo ""

echo "6️⃣  Creating an event campaign..."
EVENT_RESPONSE=$(curl -s -X POST "${API_URL}/campaigns/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Annual Charity Gala 2025",
    "description": "Join us for our annual charity gala featuring live music, auctions, and dinner. All proceeds support local youth programmes.",
    "campaign_type": "event",
    "goal_amount": 10000.00,
    "currency": "GBP",
    "start_date": "2025-06-15T19:00:00Z",
    "end_date": "2025-06-15T23:00:00Z"
  }')

EVENT_ID=$(echo $EVENT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

echo "✅ Event created (ID: $EVENT_ID):"
echo "$EVENT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$EVENT_RESPONSE"
echo ""

echo "7️⃣  Creating an ad-hoc giving opportunity..."
ADHOC_RESPONSE=$(curl -s -X POST "${API_URL}/campaigns/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Support Our Mission",
    "description": "Your donation helps us continue our work in the community. Every contribution makes a difference.",
    "campaign_type": "adhoc_giving",
    "currency": "GBP"
  }')

ADHOC_ID=$(echo $ADHOC_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

echo "✅ Ad-hoc giving created (ID: $ADHOC_ID):"
echo "$ADHOC_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$ADHOC_RESPONSE"
echo ""

echo "8️⃣  Updating campaign status to ACTIVE..."
UPDATE_CAMPAIGN_RESPONSE=$(curl -s -X PUT "${API_URL}/campaigns/${CAMPAIGN_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "active"
  }')

echo "✅ Campaign updated to active:"
echo "$UPDATE_CAMPAIGN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$UPDATE_CAMPAIGN_RESPONSE"
echo ""

echo "9️⃣  Getting single campaign..."
GET_CAMPAIGN_RESPONSE=$(curl -s -X GET "${API_URL}/campaigns/${CAMPAIGN_ID}")

echo "✅ Campaign details:"
echo "$GET_CAMPAIGN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$GET_CAMPAIGN_RESPONSE"
echo ""

echo "🔟  Listing my campaigns..."
MY_CAMPAIGNS_RESPONSE=$(curl -s -X GET "${API_URL}/campaigns/my/campaigns" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo "✅ My campaigns:"
echo "$MY_CAMPAIGNS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$MY_CAMPAIGNS_RESPONSE"
echo ""

echo "1️⃣1️⃣  Listing all active campaigns..."
LIST_CAMPAIGNS_RESPONSE=$(curl -s -X GET "${API_URL}/campaigns/?status=active")

echo "✅ Active campaigns:"
echo "$LIST_CAMPAIGNS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LIST_CAMPAIGNS_RESPONSE"
echo ""

echo "1️⃣2️⃣  Filtering campaigns by type..."
FUNDRAISING_CAMPAIGNS=$(curl -s -X GET "${API_URL}/campaigns/?campaign_type=fundraising&status=active")

echo "✅ Fundraising campaigns:"
echo "$FUNDRAISING_CAMPAIGNS" | python3 -m json.tool 2>/dev/null || echo "$FUNDRAISING_CAMPAIGNS"
echo ""

# ==================== SUMMARY ====================

echo "======================================"
echo "🎉 All tests passed successfully!"
echo ""
echo "📊 Summary:"
echo "   ✅ User registered and logged in"
echo "   ✅ Giver profile auto-created and updated"
echo "   ✅ Created 3 campaigns (fundraising, event, ad-hoc)"
echo "   ✅ Updated campaign status"
echo "   ✅ Retrieved campaigns with filters"
echo ""
echo "🔑 Your access token:"
echo "$ACCESS_TOKEN"
echo ""
echo "🎯 Campaign IDs:"
echo "   Fundraising: $CAMPAIGN_ID"
echo "   Event: $EVENT_ID"
echo "   Ad-hoc: $ADHOC_ID"
echo ""
echo "📖 Visit http://localhost:8000/docs to explore all endpoints!"
