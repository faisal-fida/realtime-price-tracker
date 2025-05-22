import pytest
from httpx import AsyncClient
from fastapi import status

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

USER_EMAIL = "itemuser@example.com"
USER_PASSWORD = "itempassword123"
USER_FULL_NAME = "Item Test User"

async def register_and_login_user_for_items_test(client: AsyncClient):
    """Helper to register a user for item tests if not already done."""
    # Try to login first, if it works, user is already registered.
    login_data = {"username": USER_EMAIL, "password": USER_PASSWORD}
    login_response = await client.post("/api/v1/login/access-token", data=login_data)
    
    if login_response.status_code == status.HTTP_401_UNAUTHORIZED:
        # User not registered or wrong password, try registering
        user_data = {
            "email": USER_EMAIL,
            "password": USER_PASSWORD,
            "full_name": USER_FULL_NAME
        }
        reg_response = await client.post("/api/v1/users/", json=user_data)
        assert reg_response.status_code == status.HTTP_201_CREATED, "Item test user registration failed"
        
        # Now login again
        login_response = await client.post("/api/v1/login/access-token", data=login_data)
    
    assert login_response.status_code == status.HTTP_200_OK, "Login failed for item test user"
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_create_item(client: AsyncClient):
    """Test creating a new item."""
    auth_headers = await register_and_login_user_for_items_test(client)
    
    item_data = {
        "url": "http://example.com/product123",
        "desired_price": 99.99
    }
    response = await client.post("/api/v1/items/", json=item_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["url"] == item_data["url"]
    assert response_data["desired_price"] == item_data["desired_price"]
    assert "id" in response_data
    assert "owner_id" in response_data # Ensure owner_id is present

async def test_get_items(client: AsyncClient):
    """Test retrieving items for a user."""
    auth_headers = await register_and_login_user_for_items_test(client)

    # Create an item first to ensure there's something to retrieve
    item_data_for_get = {
        "url": "http://example.com/product_for_get_test",
        "desired_price": 49.99
    }
    create_response = await client.post("/api/v1/items/", json=item_data_for_get, headers=auth_headers)
    assert create_response.status_code == status.HTTP_201_CREATED
    created_item_id = create_response.json()["id"]

    response = await client.get("/api/v1/items/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert isinstance(response_data, list)
    # Check if the created item is in the list
    found_item = any(item["id"] == created_item_id and item["url"] == item_data_for_get["url"] for item in response_data)
    assert found_item, "Created item not found in the list of items"

async def test_delete_item(client: AsyncClient):
    """Test deleting an item."""
    auth_headers = await register_and_login_user_for_items_test(client)

    # Create an item to delete
    item_data_for_delete = {
        "url": "http://example.com/product_to_delete",
        "desired_price": 10.00
    }
    create_response = await client.post("/api/v1/items/", json=item_data_for_delete, headers=auth_headers)
    assert create_response.status_code == status.HTTP_201_CREATED
    item_to_delete_id = create_response.json()["id"]

    # Delete the item
    delete_response = await client.delete(f"/api/v1/items/{item_to_delete_id}", headers=auth_headers)
    assert delete_response.status_code == status.HTTP_200_OK # As per Item API endpoint
    deleted_item_data = delete_response.json()
    assert deleted_item_data["id"] == item_to_delete_id
    assert deleted_item_data["url"] == item_data_for_delete["url"]

    # Try to get the deleted item
    get_response_deleted = await client.get(f"/api/v1/items/{item_to_delete_id}", headers=auth_headers)
    assert get_response_deleted.status_code == status.HTTP_404_NOT_FOUND
    assert "Item not found" in get_response_deleted.json()["detail"]
