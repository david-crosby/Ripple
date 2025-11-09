# Testing Documentation

Comprehensive guide to testing the Ripple FundRaiser backend.

## Table of Contents
- [Overview](#overview)
- [Test Framework](#test-framework)
- [Running Tests](#running-tests)
- [Test Scripts](#test-scripts)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)

## Overview

The backend uses a multi-layered testing approach:
- **Unit Tests**: Test individual functions and validation logic
- **Integration Tests**: Test API endpoints with database
- **Manual Test Scripts**: Shell scripts for quick manual testing

## Test Framework

### Technologies
- **pytest**: Testing framework
- **TestClient**: FastAPI's test client for HTTP testing
- **SQLite**: In-memory database for tests
- **httpx**: HTTP client for async testing

### Test Structure
```
backend/tests/
├── __init__.py
├── conftest.py           # Shared fixtures and configuration
├── test_auth.py          # Authentication endpoint tests
└── test_security.py      # Security feature tests (password, rate limiting)
```

## Running Tests

### Run All Tests
```bash
cd backend
pytest
```

### Run Specific Test File
```bash
pytest tests/test_auth.py
pytest tests/test_security.py
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test Function
```bash
pytest tests/test_auth.py::test_register_success
pytest tests/test_security.py::TestPasswordValidation::test_valid_password
```

### Run with Coverage Report
```bash
pytest --cov=. --cov-report=html
# View coverage report in htmlcov/index.html
```

### Run with Detailed Output
```bash
pytest -vv --tb=short
```

## Test Scripts

The backend includes several manual test scripts for quick testing:

### Authentication Tests
```bash
./test_auth.sh
```

Tests registration, login, and protected endpoint access.

**What it tests:**
- User registration
- User login
- JWT token retrieval
- Protected endpoint access with token
- Token expiration handling

### Campaign Tests
```bash
./test_campaigns.sh
```

Comprehensive test covering campaigns, donations, and givers.

**What it tests:**
- Campaign creation (fundraising, event, adhoc)
- Campaign listing and filtering
- Campaign updates
- Donation creation
- Anonymous donations
- Giver profile management
- Leaderboard functionality

### Donation Tests
```bash
./test_donations.sh
```

Focused tests for donation functionality.

**What it tests:**
- Creating donations
- Listing campaign donations
- Payment status updates
- Anonymous donation handling
- Donation history retrieval

### Security Tests (Manual)
```bash
./test_security_manual.sh
```

Manual tests for password validation and rate limiting.

**What it tests:**
- Weak password rejection (too short, no uppercase, no numbers)
- Strong password acceptance
- Invalid username rejection
- Rate limiting on login (10 requests/minute)

### Database Cleanup
```bash
./cleanup_db.sh
```

Removes test data from the database.

**What it removes:**
- Test users (username starting with `testuser_`)
- Associated giver profiles
- Associated campaigns
- Associated donations

## Automated Test Suites

### Authentication Tests (`tests/test_auth.py`)

**Test Coverage:**
- ✅ Successful user registration
- ✅ Duplicate email rejection
- ✅ Duplicate username rejection
- ✅ Invalid email format rejection
- ✅ Short password rejection
- ✅ Successful login
- ✅ Invalid credentials rejection
- ✅ Non-existent user rejection
- ✅ Authenticated user access
- ✅ Unauthenticated access rejection

**Run:**
```bash
pytest tests/test_auth.py -v
```

### Security Tests (`tests/test_security.py`)

**Test Coverage:**

**Password Validation:**
- ✅ Valid strong passwords
- ✅ Too short passwords rejection
- ✅ Missing uppercase rejection
- ✅ Missing lowercase rejection
- ✅ Missing numbers rejection
- ✅ Common password rejection

**Username Validation:**
- ✅ Valid username formats
- ✅ Too short username rejection
- ✅ Too long username rejection
- ✅ Invalid characters rejection
- ✅ Starting with number rejection

**Registration Endpoint:**
- ✅ Weak password rejection
- ✅ Strong password acceptance
- ✅ Invalid username rejection

**Rate Limiting:**
- ✅ Login rate limit enforcement (10/minute)
- ✅ Registration rate limit enforcement (5/hour)

**Run:**
```bash
pytest tests/test_security.py -v
```

## Writing Tests

### Test Fixtures

Available fixtures (defined in `conftest.py`):

#### `db`
Fresh database for each test with automatic cleanup.
```python
def test_example(db):
    # db is a SQLAlchemy session
    user = User(email="test@example.com")
    db.add(user)
    db.commit()
```

#### `client`
TestClient with test database and rate limiting disabled.
```python
def test_example(client):
    response = client.post("/auth/register", json={...})
    assert response.status_code == 201
```

#### `test_user_data`
Standard test user data dictionary.
```python
def test_example(test_user_data):
    # test_user_data = {
    #     "email": "test@example.com",
    #     "username": "testuser",
    #     "password": "TestPass123!",
    #     "full_name": "Test User"
    # }
    assert test_user_data["email"] == "test@example.com"
```

#### `authenticated_client`
TestClient with authenticated user and JWT token.
```python
def test_protected_endpoint(authenticated_client):
    response = authenticated_client.get("/auth/me")
    assert response.status_code == 200
```

### Example Test

```python
import pytest
from fastapi.testclient import TestClient

def test_user_registration(client):
    """Test successful user registration."""
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "SecurePass123",
        "full_name": "New User"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "hashed_password" not in data  # Security check

def test_duplicate_email(client, test_user_data):
    """Test that duplicate emails are rejected."""
    # Register first user
    client.post("/auth/register", json=test_user_data)

    # Try to register with same email
    response = client.post("/auth/register", json=test_user_data)

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]
```

### Testing Rate Limiting

Rate limiting tests require special handling:

```python
def test_rate_limiting(self):
    """Test login rate limit (10/minute)."""
    from main import app
    from fastapi.testclient import TestClient

    # Enable rate limiting for this test
    app.state.limiter.enabled = True

    with TestClient(app) as test_client:
        responses = []
        for i in range(11):  # Exceed limit of 10
            response = test_client.post("/auth/login", data={
                "username": "test",
                "password": "test"
            })
            responses.append(response)

        # Check that at least one request was rate limited
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes

    # Disable rate limiting again
    app.state.limiter.enabled = False
```

## Test Coverage

### Current Coverage

```
Module              Coverage
------------------  ---------
auth.py             95%
schemas.py          90%
models.py           85%
routers/auth.py     92%
utils/validation.py 100%
main.py             80%
```

### Viewing Coverage Report

Generate HTML coverage report:
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

Generate terminal coverage report:
```bash
pytest --cov=. --cov-report=term-missing
```

## Continuous Integration

### Pre-commit Checks

Before committing, run:
```bash
# Run all tests
pytest

# Check test coverage
pytest --cov=. --cov-report=term

# Run security tests specifically
pytest tests/test_security.py -v
```

### Recommended CI Pipeline

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -e .

      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Common Issues

**Issue: "Rate limit exceeded" in tests**
```
Solution: Rate limiting is disabled in conftest.py for regular tests.
If you see this error, check that the test is using the `client` fixture.
```

**Issue: Database errors in tests**
```
Solution: Each test gets a fresh database. Make sure you're not
relying on data from previous tests.
```

**Issue: "Could not import module"**
```
Solution: Run pytest from the backend directory:
cd backend
pytest
```

**Issue: Tests pass locally but fail in CI**
```
Solution: Check that all dependencies are listed in pyproject.toml
and that the CI environment matches your local Python version.
```

### Debug Mode

Run tests with detailed output:
```bash
pytest -vv --tb=long --log-cli-level=DEBUG
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Clear Names**: Test names should describe what they test
3. **AAA Pattern**: Arrange, Act, Assert
4. **Fixtures**: Use fixtures for common setup
5. **Coverage**: Aim for >85% code coverage
6. **Fast Tests**: Keep individual tests fast (<1 second)
7. **Descriptive Asserts**: Use clear assertion messages

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [SECURITY.md](SECURITY.md) - Security testing documentation
- [AUTHENTICATION.md](AUTHENTICATION.md) - Authentication testing examples
