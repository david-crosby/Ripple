"""
Tests for authentication endpoints.

Tests registration, login, and current user retrieval.
"""

import pytest


def test_register_success(client, test_user_data):
    """Test successful user registration."""
    response = client.post("/auth/register", json=test_user_data)
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify user data
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]
    assert data["full_name"] == test_user_data["full_name"]
    assert data["is_active"] is True
    
    # Ensure password is not returned
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client, test_user_data):
    """Test that registration fails with duplicate email."""
    # Register first user
    client.post("/auth/register", json=test_user_data)
    
    # Try to register with same email but different username
    duplicate_data = test_user_data.copy()
    duplicate_data["username"] = "different_username"
    
    response = client.post("/auth/register", json=duplicate_data)
    
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


def test_register_duplicate_username(client, test_user_data):
    """Test that registration fails with duplicate username."""
    # Register first user
    client.post("/auth/register", json=test_user_data)
    
    # Try to register with same username but different email
    duplicate_data = test_user_data.copy()
    duplicate_data["email"] = "different@example.com"
    
    response = client.post("/auth/register", json=duplicate_data)
    
    assert response.status_code == 400
    assert "username" in response.json()["detail"].lower()


def test_register_invalid_email(client, test_user_data):
    """Test that registration fails with invalid email."""
    test_user_data["email"] = "invalid-email"
    
    response = client.post("/auth/register", json=test_user_data)
    
    assert response.status_code == 422  # Pydantic validation error


def test_register_short_password(client, test_user_data):
    """Test that registration fails with short password."""
    test_user_data["password"] = "short"
    
    response = client.post("/auth/register", json=test_user_data)
    
    assert response.status_code == 422


def test_login_success(client, test_user_data):
    """Test successful login."""
    # Register user first
    client.post("/auth/register", json=test_user_data)
    
    # Login
    response = client.post(
        "/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_invalid_credentials(client, test_user_data):
    """Test that login fails with incorrect password."""
    # Register user
    client.post("/auth/register", json=test_user_data)
    
    # Try to login with wrong password
    response = client.post(
        "/auth/login",
        data={
            "username": test_user_data["email"],
            "password": "WrongPassword123!"
        }
    )
    
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test that login fails for non-existent user."""
    response = client.post(
        "/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "SomePassword123!"
        }
    )
    
    assert response.status_code == 401


def test_get_current_user_authenticated(authenticated_client, test_user_data):
    """Test retrieving current user info when authenticated."""
    response = authenticated_client.get("/auth/me")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]


def test_get_current_user_unauthenticated(client):
    """Test that getting current user fails without authentication."""
    response = client.get("/auth/me")
    
    assert response.status_code == 401