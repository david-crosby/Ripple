#!/bin/bash
# Manual test script for security features
# Run this after starting the server to verify password validation and rate limiting

BASE_URL="http://localhost:8000"

echo "========================================="
echo "Security Features Test Script"
echo "========================================="
echo ""

# Test 1: Weak password (too short)
echo "Test 1: Registration with weak password (too short)"
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test1@example.com",
    "username": "testuser1",
    "password": "weak",
    "full_name": "Test User"
  }' | jq '.detail[0].msg' || echo "Failed"
echo ""
echo ""

# Test 2: Password without uppercase
echo "Test 2: Registration with password missing uppercase"
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "username": "testuser2",
    "password": "lowercase123",
    "full_name": "Test User"
  }' | jq '.detail[0].msg' || echo "Failed"
echo ""
echo ""

# Test 3: Password without number
echo "Test 3: Registration with password missing number"
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test3@example.com",
    "username": "testuser3",
    "password": "NoNumbers",
    "full_name": "Test User"
  }' | jq '.detail[0].msg' || echo "Failed"
echo ""
echo ""

# Test 4: Valid strong password (should succeed)
echo "Test 4: Registration with strong password (should succeed)"
TIMESTAMP=$(date +%s)
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"user${TIMESTAMP}@example.com\",
    \"username\": \"user${TIMESTAMP}\",
    \"password\": \"SecurePass123\",
    \"full_name\": \"Test User\"
  }" | jq '.email // .detail' || echo "Failed"
echo ""
echo ""

# Test 5: Invalid username (starts with number)
echo "Test 5: Registration with invalid username (starts with number)"
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test5@example.com",
    "username": "123invalid",
    "password": "SecurePass123",
    "full_name": "Test User"
  }' | jq '.detail[0].msg' || echo "Failed"
echo ""
echo ""

# Test 6: Rate limiting on login
echo "Test 6: Rate limiting on login (making 12 login attempts)"
echo "You should see rate limit errors (429) after 10 attempts..."
for i in {1..12}; do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/auth/login" \
    -d "username=testuser&password=testpass")

  if [ "$HTTP_CODE" == "429" ]; then
    echo "  Attempt $i: RATE LIMITED (429) ✓"
  elif [ "$HTTP_CODE" == "401" ]; then
    echo "  Attempt $i: Unauthorized (401) - Expected"
  else
    echo "  Attempt $i: HTTP $HTTP_CODE"
  fi
done
echo ""

echo "========================================="
echo "Security Tests Complete!"
echo "========================================="
echo ""
echo "Expected results:"
echo "- Tests 1-3, 5: Should show validation errors"
echo "- Test 4: Should succeed and return user data"
echo "- Test 6: Should show 429 (rate limited) after 10 attempts"
