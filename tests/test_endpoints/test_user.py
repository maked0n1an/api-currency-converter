import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    payload = {
        "email": "user2@example.com",
        "username": "testuser",
        "password": "ValidPassWord@123",
    }
    response = await client.post("/user/register", json=payload)
    data = response.json()

    assert response.status_code == 201
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_user(client: AsyncClient, create_user_in_db, db_user):
    await create_user_in_db(**db_user)
    payload = {
        "email": "user@example.com",
        "username": "niceactor",
        "password": "HelloNigga-71"
    }

    response = await client.post("/user/register", json=payload)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "User with 'niceactor' username or 'user@example.com' email exists"
    }


@pytest.mark.asyncio
async def test_complete_profile(client: AsyncClient, authed_user):
    client.cookies = authed_user["cookies"]
    payload = {"first_name": "John", "last_name": "Doe"}

    response = await client.put(
        "/user/complete_profile",
        json=payload,
        headers={
            "Authorization": authed_user["headers"]["Authorization"]
        }
    )
    data = response.json()

    assert response.status_code == 200
    assert data["first_name"] == payload["first_name"]
    assert data["last_name"] == payload["last_name"]


@pytest.mark.asyncio
async def test_about_me(client: AsyncClient, test_user_data, authed_user):
    client.cookies = authed_user["cookies"]

    response = await client.get(
        "/user/about_me",
        headers={
            "Authorization": authed_user["headers"]["Authorization"]
        }
    )
    data = response.json()

    assert response.status_code == 200
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]


@pytest.mark.asyncio
async def test_about_me_unauthorized(client: AsyncClient):
    response = await client.get("/user/about_me")
    assert response.status_code == 401
