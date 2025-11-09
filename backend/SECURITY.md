# Security Features

This document outlines the security features implemented in the Ripple FundRaiser backend.

## Password Validation

The backend enforces strong password requirements to protect user accounts:

### Requirements
- **Minimum length**: 8 characters
- **Uppercase letter**: At least one (A-Z)
- **Lowercase letter**: At least one (a-z)
- **Number**: At least one digit (0-9)
- **Common password check**: Rejects commonly used passwords

### Implementation
Password validation is implemented in two places:

1. **Schema validation** ([schemas.py:29-37](backend/schemas.py#L29-L37))
   - Pydantic validators automatically check password strength on registration
   - Validation happens before the request reaches the database

2. **Validation utility** ([utils/validation.py:11-56](backend/utils/validation.py#L11-L56))
   - Reusable `validate_password_strength()` function
   - Can be used for password reset and change operations

### Example Passwords

**Valid Passwords** ✅
```
SecurePass123
MyP@ssw0rd!
Tr0ub4dor&3
C0mpl3x_P@ss
Str0ng!Pass
```

**Invalid Passwords** ❌
```
password        → Too common
short1A         → Too short (less than 8 characters)
noupppercase1   → No uppercase letter
NOLOWERCASE1    → No lowercase letter
NoNumbers       → No numbers
password123     → Common password (even with numbers)
Password123     → Common password (lowercase version is common)
12345678        → Common password (all numbers)
qwerty123       → Common password
Letmein1        → Common password
```

### Common Passwords List

The following passwords are rejected (case-insensitive):
- password, password123
- 12345678, 1234567890
- qwerty, abc123
- monkey, letmein
- trustno1, dragon
- baseball, iloveyou
- master, sunshine, ashley

**Note**: In production, consider using the `zxcvbn` library for more comprehensive password strength checking.

## Rate Limiting

Rate limiting protects against brute force attacks and abuse by limiting the number of requests from a single IP address.

### Implementation
We use **SlowAPI**, a rate limiting library for FastAPI that's based on Flask-Limiter.

### Endpoints Protected

| Endpoint | Rate Limit | Purpose |
|----------|-----------|---------|
| `POST /auth/register` | 5 per hour | Prevent mass account creation |
| `POST /auth/login` | 10 per minute | Prevent brute force password attacks |

### Configuration
Rate limiting is configured in:
- **Global setup**: [main.py:42-55](backend/main.py#L42-L55)
- **Endpoint decorators**: [routers/auth.py:45,120](backend/routers/auth.py#L45)

### How It Works
1. Each request's IP address is tracked using `get_remote_address()`
2. Request counters are stored in memory
3. When limit is exceeded, returns HTTP 429 (Too Many Requests)
4. Limits reset after the specified time window

### Response Examples

**When rate limit is exceeded (HTTP 429):**
```json
{
  "error": "Rate limit exceeded: 5 per 1 hour"
}
```

**Response headers include rate limit information:**
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1699200000
Retry-After: 3600
```

### How Rate Limits Reset

Rate limits use a sliding window approach:
- **Registration (5/hour)**: Limit resets 60 minutes after first request
- **Login (10/minute)**: Limit resets 60 seconds after first request

**Example Timeline:**
```
10:00:00 - First registration request (count: 1/5)
10:15:00 - Second registration request (count: 2/5)
10:30:00 - Third registration request (count: 3/5)
11:00:00 - First request limit resets (count: 2/5)
11:15:00 - Second request limit resets (count: 1/5)
```

### Customizing Rate Limits
To adjust rate limits, modify the decorator on the endpoint:

```python
@limiter.limit("20/minute")  # Allow 20 requests per minute
def my_endpoint(request: Request):
    ...
```

Common patterns:
- `"10/second"` - 10 requests per second
- `"100/minute"` - 100 requests per minute
- `"1000/hour"` - 1000 requests per hour
- `"10000/day"` - 10000 requests per day

## Additional Security Measures

### Password Hashing
- Uses **bcrypt** for password hashing ([auth.py:37-56](backend/auth.py#L37-L56))
- Automatic salt generation
- Configurable work factor for future-proofing

### JWT Tokens
- Uses **HS256** algorithm for token signing
- Configurable expiration time (default: 30 minutes)
- Secret key stored in environment variables

### Database Security
- Passwords are **never** stored in plain text
- User responses exclude sensitive fields
- Parameterized queries prevent SQL injection

### Username Validation
- Must be 3-50 characters
- Must start with a letter
- Only alphanumeric and underscores allowed
- Prevents username enumeration through timing attacks

## Environment Variables

Security-related environment variables (add to `.env`):

```bash
# JWT Configuration
SECRET_KEY=your-secret-key-here  # Use a strong random string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (with secure password)
DATABASE_URL=mysql+pymysql://user:secure_password@localhost/fundraiser_db
```

## Best Practices

1. **Never commit `.env` files** - Keep secrets out of version control
2. **Use strong SECRET_KEY** - Generate using `openssl rand -hex 32`
3. **Enable HTTPS** - Always use TLS/SSL in production
4. **Regular updates** - Keep dependencies updated for security patches
5. **Monitor rate limits** - Adjust based on legitimate usage patterns

## Testing Security Features

### Automated Tests

Run the comprehensive test suite:
```bash
cd backend
pytest tests/test_security.py -v
```

This will test:
- Password strength validation
- Username format validation
- Registration endpoint with various passwords
- Rate limiting on login and registration

### Manual Testing

Use the provided test script:
```bash
cd backend
bash test_security_manual.sh
```

Or test manually with curl:

**Test password validation:**
```bash
# Should fail - weak password
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"weak"}'

# Should succeed - strong password
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"SecurePass123"}'
```

**Test rate limiting:**
```bash
# Run this script to exceed login rate limit
for i in {1..15}; do
  curl -X POST http://localhost:8000/auth/login \
    -d "username=test&password=test"
  echo "Request $i"
done
```

## Future Enhancements

Consider implementing:
- [ ] Account lockout after multiple failed login attempts
- [ ] Email verification for new accounts
- [ ] Two-factor authentication (2FA)
- [ ] Password reset with email confirmation
- [ ] CAPTCHA for registration
- [ ] IP whitelist/blacklist
- [ ] Request logging and monitoring
- [ ] Redis-backed rate limiting for distributed systems
