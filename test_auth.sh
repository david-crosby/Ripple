#!/bin/zsh

# Quick authentication test script
# This script tests the complete authentication flow

set -e  # Exit on error

API_URL="http://localhost:8000"

echo "🧪 Testing Authentication Flow"
echo "================================"
echo ""

# Generate random username to avoid conflicts
RANDOM_NUM=$RANDOM
USERNAME="testuser${RANDOM_NUM}"
EMAIL="test${RANDOM_NUM}@example.com"
PASSWORD="testpass123"

echo "📝 Test credentials:"
echo "   Username: $USERNAME"
echo "   Email: $EMAIL"
echo "   Password: $PASSWORD"
echo ""

# 1. Register
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

echo "✅ Registration successful!"
echo "$REGISTER_BODY" | python3 -m json.tool 2>/dev/null || echo "$REGISTER_BODY"
echo ""

# 2. Login
echo "2️⃣  Logging in..."
TOKEN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${USERNAME}&password=${PASSWORD}")

# Extract access token
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Login failed!"
    echo "$TOKEN_RESPONSE"
    exit 1
fi

echo "✅ Login successful!"
echo "🔑 Access token: ${ACCESS_TOKEN:0:50}..."
echo ""

# 3. Get current user
echo "3️⃣  Getting current user info..."
USER_INFO=$(curl -s -X GET "${API_URL}/auth/me" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo "✅ Current user:"
echo "$USER_INFO" | python3 -m json.tool 2>/dev/null || echo "$USER_INFO"
echo ""

# 4. Test protected endpoint
echo "4️⃣  Testing protected endpoint..."
PROTECTED_RESPONSE=$(curl -s -X GET "${API_URL}/protected" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo "✅ Protected endpoint response:"
echo "$PROTECTED_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$PROTECTED_RESPONSE"
echo ""

# 5. Test without token (should fail)
echo "5️⃣  Testing protected endpoint WITHOUT token (should fail)..."
UNAUTHORIZED_RESPONSE=$(curl -s -X GET "${API_URL}/protected")

echo "✅ Correctly rejected (401):"
echo "$UNAUTHORIZED_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$UNAUTHORIZED_RESPONSE"
echo ""

echo "================================"
echo "🎉 All authentication tests passed!"
echo ""
echo "💡 Your access token (save this for testing):"
echo "$ACCESS_TOKEN"
echo ""
echo "📖 For more details, see AUTHENTICATION.md"
