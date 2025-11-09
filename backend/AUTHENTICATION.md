# Authentication Testing Guide

Quick guide to test the authentication endpoints.

## Security Features

⚠️ **Important**: The authentication endpoints have security features enabled:

### Password Requirements
Passwords must meet these requirements:
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one number (0-9)
- Cannot be a common password

### Rate Limiting
- **Registration**: Limited to 5 attempts per hour per IP
- **Login**: Limited to 10 attempts per minute per IP
- Exceeding limits returns HTTP 429 (Too Many Requests)

See [SECURITY.md](SECURITY.md) for complete security documentation.

## Available Endpoints

### 1. Register a New User
**POST** `/auth/register` - **Rate Limited: 5/hour**

**Password Requirements**: Must include uppercase, lowercase, and numbers.

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123",
    "full_name": "Test User"
  }'
```

**Success Response (201):**
```json
{
  "id": 1,
  "email": "test@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-11-05T10:30:00"
}
```

**Validation Error Response (422):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "password"],
      "msg": "Value error, Password must contain at least one uppercase letter",
      "input": "weakpassword"
    }
  ]
}
```

**Rate Limit Error Response (429):**
```json
{
  "error": "Rate limit exceeded: 5 per 1 hour"
}
```

### 2. Login
**POST** `/auth/login` - **Rate Limited: 10/minute**

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=SecurePass123"
```

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Invalid Credentials Response (401):**
```json
{
  "detail": "Incorrect username or password"
}
```

**Rate Limit Error Response (429):**
```json
{
  "error": "Rate limit exceeded: 10 per 1 minute"
}
```

### 3. Get Current User Info
**GET** `/auth/me`

```bash
# Replace YOUR_TOKEN with the access_token from login
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "email": "test@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-11-05T10:30:00"
}
```

### 4. Test Protected Endpoint
**GET** `/protected`

```bash
curl -X GET "http://localhost:8000/protected" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "message": "Hello testuser!",
  "user_id": 1,
  "email": "test@example.com"
}
```

## Using Swagger UI (Recommended)

1. Go to http://localhost:8000/docs
2. Click on `/auth/register` and try registering a user
3. Click on `/auth/login` and get your access token
4. Click the **Authorize** button at the top right
5. Enter your token in the format: `Bearer YOUR_TOKEN`
6. Now you can test all protected endpoints!

## Testing Flow

### Full Authentication Flow:

```bash
# 1. Register a new user
REGISTER_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "username": "demo",
    "password": "demopass123",
    "full_name": "Demo User"
  }')

echo "Registration response:"
echo $REGISTER_RESPONSE | jq

# 2. Login and get token
TOKEN_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demopass123")

# Extract the access token
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

echo "Access token: $ACCESS_TOKEN"

# 3. Get current user info
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

# 4. Test protected endpoint
curl -X GET "http://localhost:8000/protected" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

## Common Errors

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```
**Solution:** Check your token is valid and properly formatted in the Authorization header.

### 400 Bad Request
```json
{
  "detail": "Username already registered"
}
```
**Solution:** Choose a different username or email.

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address"
    }
  ]
}
```
**Solution:** Check your request data matches the expected schema.

## Security Notes

- **Never commit your `.env` file** - it contains your SECRET_KEY
- **Generate a secure SECRET_KEY** for production: `openssl rand -hex 32`
- **Use HTTPS** in production
- **Tokens expire** after 30 minutes (configurable in `.env`)
- **Passwords are hashed** using bcrypt before storage

## Next Steps

Now that authentication is working, you can:
1. Add email verification
2. Implement password reset
3. Add refresh tokens for longer sessions
4. Create Campaign and Donation endpoints
5. Add role-based access control (admin, user, etc.)
