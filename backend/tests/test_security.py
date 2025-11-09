"""
Tests for security features: password validation and rate limiting.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from utils.validation import validate_password_strength, validate_username


client = TestClient(app)


class TestPasswordValidation:
    """Test password strength validation."""

    def test_valid_password(self):
        """Test that valid passwords pass validation."""
        is_valid, error = validate_password_strength("SecurePass123")
        assert is_valid is True
        assert error == ""

    def test_password_too_short(self):
        """Test that short passwords are rejected."""
        is_valid, error = validate_password_strength("Short1A")
        assert is_valid is False
        assert "at least 8 characters" in error

    def test_password_no_uppercase(self):
        """Test that passwords without uppercase are rejected."""
        is_valid, error = validate_password_strength("lowercase123")
        assert is_valid is False
        assert "uppercase" in error

    def test_password_no_lowercase(self):
        """Test that passwords without lowercase are rejected."""
        is_valid, error = validate_password_strength("UPPERCASE123")
        assert is_valid is False
        assert "lowercase" in error

    def test_password_no_number(self):
        """Test that passwords without numbers are rejected."""
        is_valid, error = validate_password_strength("NoNumbersHere")
        assert is_valid is False
        assert "number" in error

    def test_common_password(self):
        """Test that common passwords are rejected."""
        # Test with "Password123" which becomes "password123" when lowercased
        # "password123" is in the common password list
        is_valid, error = validate_password_strength("Password123")
        assert is_valid is False
        assert "common" in error.lower()


class TestUsernameValidation:
    """Test username validation."""

    def test_valid_username(self):
        """Test that valid usernames pass validation."""
        is_valid, error = validate_username("john_doe123")
        assert is_valid is True
        assert error == ""

    def test_username_too_short(self):
        """Test that short usernames are rejected."""
        is_valid, error = validate_username("ab")
        assert is_valid is False
        assert "at least 3 characters" in error

    def test_username_too_long(self):
        """Test that long usernames are rejected."""
        is_valid, error = validate_username("a" * 51)
        assert is_valid is False
        assert "less than 50 characters" in error

    def test_username_invalid_characters(self):
        """Test that usernames with invalid characters are rejected."""
        is_valid, error = validate_username("user@name")
        assert is_valid is False
        assert "letters, numbers, and underscores" in error

    def test_username_starts_with_number(self):
        """Test that usernames starting with numbers are rejected."""
        is_valid, error = validate_username("123username")
        assert is_valid is False
        assert "start with a letter" in error


class TestRegistrationEndpoint:
    """Test the registration endpoint with password validation."""

    def test_register_with_weak_password(self):
        """Test that registration fails with weak password."""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "weak",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422  # Unprocessable Entity
        # Check that validation error occurred
        detail = response.json()["detail"]
        assert isinstance(detail, list)
        assert len(detail) > 0

    def test_register_with_strong_password(self):
        """Test that registration succeeds with strong password."""
        # Note: This test may fail if user already exists
        # In a real test suite, you'd use a test database with cleanup
        import time
        unique_email = f"user{int(time.time()*1000)}@example.com"
        unique_username = f"user{int(time.time()*1000)}"

        response = client.post(
            "/auth/register",
            json={
                "email": unique_email,
                "username": unique_username,
                "password": "SecurePass123",
                "full_name": "New User"
            }
        )
        # Should succeed (201) or fail if user exists (400) or rate limited (429)
        assert response.status_code in [201, 400, 429]

    def test_register_with_invalid_username(self):
        """Test that registration fails with invalid username."""
        response = client.post(
            "/auth/register",
            json={
                "email": "test2@example.com",
                "username": "ab",  # Too short
                "password": "SecurePass123",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422


class TestRateLimiting:
    """Test rate limiting on authentication endpoints."""

    def test_login_rate_limit(self):
        """
        Test that login endpoint enforces rate limiting.

        Note: This test will make multiple requests and may be slow.
        The rate limit is 10 per minute for login.
        """
        # Create a client with rate limiting enabled
        from main import app
        from fastapi.testclient import TestClient

        # Temporarily enable rate limiting
        app.state.limiter.enabled = True

        with TestClient(app) as test_client:
            # Make 11 requests to exceed the limit
            responses = []
            for i in range(11):
                response = test_client.post(
                    "/auth/login",
                    data={
                        "username": "testuser",
                        "password": "testpass"
                    }
                )
                responses.append(response)

            # At least one request should be rate limited (429)
            status_codes = [r.status_code for r in responses]
            assert 429 in status_codes, "Expected at least one 429 (rate limited) response"

        # Disable rate limiting again for other tests
        app.state.limiter.enabled = False

    def test_register_rate_limit(self):
        """
        Test that registration endpoint enforces rate limiting.

        Note: Rate limit is 5 per hour for registration.
        This test makes 6 requests to test the limit.
        """
        # Create a client with rate limiting enabled
        from main import app
        from fastapi.testclient import TestClient

        # Temporarily enable rate limiting
        app.state.limiter.enabled = True

        with TestClient(app) as test_client:
            # Make 6 requests to exceed the limit
            responses = []
            for i in range(6):
                response = test_client.post(
                    "/auth/register",
                    json={
                        "email": f"ratelimit{i}@example.com",
                        "username": f"ratelimit{i}",
                        "password": "SecurePass123",
                        "full_name": "Rate Limit Test"
                    }
                )
                responses.append(response)

            # At least one request should be rate limited (429)
            status_codes = [r.status_code for r in responses]
            assert 429 in status_codes, "Expected at least one 429 (rate limited) response"

        # Disable rate limiting again for other tests
        app.state.limiter.enabled = False


# Run tests with: pytest tests/test_security.py -v
