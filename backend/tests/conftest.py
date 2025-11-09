"""
Pytest configuration and fixtures.

This file provides reusable test fixtures for database, test client,
and authenticated sessions.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

# Use in-memory SQLite database for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db():
    """
    Provide a fresh database for each test.
    
    Creates all tables before the test and drops them after.
    This ensures each test starts with a clean database state.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Provide database session
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    """
    Provide a test client with test database.

    Overrides the get_db dependency to use the test database
    instead of the production database.
    Disables rate limiting for tests.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Disable rate limiting during tests
    app.state.limiter.enabled = False

    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    app.state.limiter.enabled = True
    app.dependency_overrides.clear()


@pytest.fixture()
def test_user_data():
    """Provide standard test user data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123!",
        "full_name": "Test User"
    }


@pytest.fixture()
def authenticated_client(client, test_user_data):
    """
    Provide an authenticated test client.
    
    Registers a test user and includes the JWT token
    in all subsequent requests.
    """
    # Register user
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 201
    
    # Login to get token
    login_response = client.post(
        "/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Add authorization header to client
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    return client