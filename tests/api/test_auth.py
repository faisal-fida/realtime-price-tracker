import pytest
from httpx import AsyncClient
from fastapi import status # For status codes

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

async def test_user_registration(client: AsyncClient):
    """Test user registration and duplicate registration."""
    user_data = {
        "email": "testuser@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    # Register a new user
    response = await client.post("/api/v1/users/", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["email"] == user_data["email"]
    assert response_data["full_name"] == user_data["full_name"]
    assert "id" in response_data
    assert response_data["is_active"] is True

    # Try registering the same user again
    response_duplicate = await client.post("/api/v1/users/", json=user_data)
    assert response_duplicate.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response_duplicate.json()["detail"]

async def test_user_login(client: AsyncClient):
    """Test user login with correct and incorrect credentials."""
    # First, ensure a user is registered (can be part of this test or a fixture)
    user_data_for_login = {
        "email": "loginuser@example.com",
        "password": "loginpassword123",
        "full_name": "Login User"
    }
    registration_response = await client.post("/api/v1/users/", json=user_data_for_login)
    assert registration_response.status_code == status.HTTP_201_CREATED, "User registration failed for login test"

    login_credentials_correct = {
        "username": user_data_for_login["email"],
        "password": user_data_for_login["password"]
    }
    # Attempt to log in with correct credentials
    response_correct = await client.post("/api/v1/login/access-token", data=login_credentials_correct)
    assert response_correct.status_code == status.HTTP_200_OK
    token_data = response_correct.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    login_credentials_incorrect = {
        "username": user_data_for_login["email"],
        "password": "wrongpassword"
    }
    # Attempt to log in with incorrect password
    response_incorrect = await client.post("/api/v1/login/access-token", data=login_credentials_incorrect)
    assert response_incorrect.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect email or password" in response_incorrect.json()["detail"]
