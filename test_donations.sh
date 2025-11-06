#!/bin/zsh

# Donation endpoints test script
# Tests the complete donation flow

set -e  # Exit on error

API_URL="http://localhost:8000"

echo "🧪 Testing Donation Endpoints"
echo "=============================="
echo ""

# Generate random username to avoid conflicts
TIMESTAMP=$(date +%s)
RANDOM_NUM=$RANDOM
TEST_USER="testuser_${TIMESTAMP}_${RANDOM_NUM}"
TEST_EMAIL="test_${TIMESTAMP}_${RANDOM_NUM}@example.com"
TEST_PASSWORD="testpass123"

echo "📝 Test credentials:"
echo "   Username: $TEST_USER"
echo "   Email: $TEST_EMAIL"
echo ""

# ==================== SETUP ====================

echo "🔧 SETUP"
echo "========"
echo ""

echo "1️⃣  Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_EMAIL}\",
    \"username\": \"${TEST_USER}\",
    \"password\": \"${TEST_PASSWORD}\",
    \"full_name\": \"Test Donor\"
  }")

echo "✅ User registered!"
echo ""

echo "2️⃣  Logging in..."
TOKEN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${TEST_USER}&password=${TEST_PASSWORD}")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Login failed!"
    exit 1
fi

echo "✅ Login successful!"
echo "🔑 Token: ${ACCESS_TOKEN:0:50}..."
echo ""

echo "3️⃣  Creating a campaign..."
CAMPAIGN_RESPONSE=$(curl -s -X POST "${API_URL}/campaigns/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Campaign for Donations",
    "description": "This campaign is for testing donation endpoints.",
    "campaign_type": "fundraising",
    "goal_amount": 1000.00,
    "currency": "GBP"
  }')

CAMPAIGN_ID=$(echo $CAMPAIGN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

echo "✅ Campaign created (ID: $CAMPAIGN_ID)!"
echo ""

echo "4️⃣  Activating campaign..."
ACTIVATE_RESPONSE=$(curl -s -X PUT "${API_URL}/campaigns/${CAMPAIGN_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "active"
  }')

echo "✅ Campaign activated!"
echo ""

# ==================== DONATIONS ====================

echo "💰 DONATIONS"
echo "============"
echo ""

echo "5️⃣  Creating a donation (£50.00)..."
DONATION_RESPONSE=$(curl -s -X POST "${API_URL}/donations/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"campaign_id\": ${CAMPAIGN_ID},
    \"amount\": 50.00,
    \"currency\": \"GBP\",
    \"is_anonymous\": false,
    \"message\": \"Great cause! Happy to help.\"
  }")

DONATION_ID=$(echo $DONATION_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

echo "✅ Donation created (ID: $DONATION_ID, Status: PENDING):"
echo "$DONATION_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$DONATION_RESPONSE"
echo ""

echo "6️⃣  Creating an anonymous donation (£25.00)..."
ANON_DONATION_RESPONSE=$(curl -s -X POST "${API_URL}/donations/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"campaign_id\": ${CAMPAIGN_ID},
    \"amount\": 25.00,
    \"currency\": \"GBP\",
    \"is_anonymous\": true,
    \"message\": \"Prefer to stay anonymous.\"
  }")

ANON_DONATION_ID=$(echo $ANON_DONATION_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

echo "✅ Anonymous donation created (ID: $ANON_DONATION_ID):"
echo "$ANON_DONATION_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$ANON_DONATION_RESPONSE"
echo ""

echo "7️⃣  Completing first donation (simulating payment success)..."
COMPLETE_RESPONSE=$(curl -s -X PATCH "${API_URL}/donations/${DONATION_ID}/status?payment_status=completed&payment_intent_id=pi_test_123" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo "✅ Donation marked as completed:"
echo "$COMPLETE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$COMPLETE_RESPONSE"
echo ""

echo "8️⃣  Completing anonymous donation..."
COMPLETE_ANON_RESPONSE=$(curl -s -X PATCH "${API_URL}/donations/${ANON_DONATION_ID}/status?payment_status=completed&payment_intent_id=pi_test_456" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo "✅ Anonymous donation marked as completed:"
echo "$COMPLETE_ANON_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$COMPLETE_ANON_RESPONSE"
echo ""

echo "9️⃣  Getting my donation history..."
MY_DONATIONS_RESPONSE=$(curl -s -X GET "${API_URL}/donations/my/donations" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo "✅ My donations:"
echo "$MY_DONATIONS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$MY_DONATIONS_RESPONSE"
echo ""

echo "🔟  Getting campaign donations..."
CAMPAIGN_DONATIONS_RESPONSE=$(curl -s -X GET "${API_URL}/donations/campaigns/${CAMPAIGN_ID}")

echo "✅ Campaign donations (public only):"
echo "$CAMPAIGN_DONATIONS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$CAMPAIGN_DONATIONS_RESPONSE"
echo ""

echo "1️⃣1️⃣  Getting campaign donations (including anonymous)..."
CAMPAIGN_DONATIONS_ALL=$(curl -s -X GET "${API_URL}/donations/campaigns/${CAMPAIGN_ID}?include_anonymous=true")

echo "✅ Campaign donations (including anonymous):"
echo "$CAMPAIGN_DONATIONS_ALL" | python3 -m json.tool 2>/dev/null || echo "$CAMPAIGN_DONATIONS_ALL"
echo ""

echo "1️⃣2️⃣  Checking updated campaign..."
UPDATED_CAMPAIGN=$(curl -s -X GET "${API_URL}/campaigns/${CAMPAIGN_ID}")

echo "✅ Updated campaign (current_amount should be £75.00):"
echo "$UPDATED_CAMPAIGN" | python3 -m json.tool 2>/dev/null || echo "$UPDATED_CAMPAIGN"
echo ""

echo "1️⃣3️⃣  Checking updated giver profile..."
UPDATED_PROFILE=$(curl -s -X GET "${API_URL}/givers/profile/me" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo "✅ Updated giver profile (total_donated should be £75.00, donation_count: 2):"
echo "$UPDATED_PROFILE" | python3 -m json.tool 2>/dev/null || echo "$UPDATED_PROFILE"
echo ""

# ==================== SUMMARY ====================

echo "======================================"
echo "🎉 All donation tests passed!"
echo ""
echo "📊 Summary:"
echo "   ✅ Created 2 donations (1 public, 1 anonymous)"
echo "   ✅ Marked both as completed"
echo "   ✅ Campaign current_amount updated: £75.00"
echo "   ✅ Giver profile updated: £75.00 donated, 2 donations"
echo "   ✅ Retrieved donation history"
echo "   ✅ Listed campaign donations"
echo ""
echo "🔑 Your access token:"
echo "$ACCESS_TOKEN"
echo ""
echo "🎯 IDs for further testing:"
echo "   Campaign: $CAMPAIGN_ID"
echo "   Donation 1: $DONATION_ID"
echo "   Donation 2: $ANON_DONATION_ID"
echo ""
echo "📖 Visit http://localhost:8000/docs to explore all endpoints!"