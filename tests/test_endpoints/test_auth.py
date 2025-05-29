import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_user, test_user_data, create_user_in_db):
    await create_user_in_db(**db_user)

    response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        },
        headers=test_user_data["headers"]
    )
    data = response.json()

    assert response.status_code == 200
    assert "access_token" in data
    assert response.cookies.get("csrf_token") is not None
    assert response.cookies.get("refresh_token") is not None


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, db_user, test_user_data, create_user_in_db):
    await create_user_in_db(**db_user)
    test_user_data["password"] = "WrongPassword1!"

    response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        },
        headers=test_user_data["headers"]
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}


@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient, authed_user):
    client.cookies = authed_user["cookies"]
    client.headers = authed_user["headers"]

    response = await client.post("/api/auth/refresh")
    data = response.json()

    assert response.status_code == 201
    assert "access_token" in data
    assert response.cookies.get("refresh_token") is not None


@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient, authed_user):
    client.cookies = authed_user["cookies"]
    client.headers = authed_user["headers"]

    response = await client.get("/api/auth/logout")
    data = response.json()

    assert response.status_code == 200
    assert data["message"] == "Logged out successfully"
    assert data["tokens_revoked"] == 1


@pytest.mark.asyncio
async def test_logout_all_success(client: AsyncClient, test_user_data):
    await client.post(
        "/api/user/register",
        json={
            "email": test_user_data["email"],
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }
    )
    
    device_ids = ["device-1", "device-2", "device-3"]
    login_cookies_headers = []

    # Login from multiple devices
    for device_id in device_ids:
        response = await client.post(
            "/api/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            },
            headers={"X-Device-ID": device_id}
        )
        
        assert response.status_code == 200
        cookies = {
            "refresh_token": response.cookies.get("refresh_token"),
            "csrf_token": response.cookies.get("csrf_token")
        }
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}",
            "X-Device-ID": device_id,
            "X-CSRF-Token": response.cookies.get("csrf_token")
        }
        login_cookies_headers.append((headers, cookies))

    # Use one device to call logout_all
    headers, cookies = login_cookies_headers[0]
    response = await client.post(
        "/api/auth/logout_all", 
        headers=headers, 
        cookies=cookies
    )
    data = response.json()

    assert response.status_code == 200
    assert data["message"] == "Logged out from all devices"
    assert data["tokens_revoked"] == len(device_ids)
