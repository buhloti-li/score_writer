import pytest

from tests.conftest import auth_header, create_test_user


class TestAuthAPI:
    """Auth API tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    async def test_register(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "phone": "13800138000",
            "password": "testpass123",
            "nickname": "TestUser",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["phone"] == "13800138000"
        assert data["nickname"] == "TestUser"
        assert "password" not in data

    async def test_login(self, client, db_session):
        # Register first
        await client.post("/api/v1/auth/register", json={
            "phone": "13800138000",
            "password": "testpass123",
        })
        # Login
        resp = await client.post("/api/v1/auth/login", json={
            "phone": "13800138000",
            "password": "testpass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_get_me(self, client, db_session):
        user = await create_test_user(db_session)
        resp = await client.get("/api/v1/auth/me", headers=auth_header(user))
        assert resp.status_code == 200
        assert resp.json()["phone"] == user.phone

    # --- Boundary cases ---
    async def test_register_with_email(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "testpass123",
        })
        assert resp.status_code == 201

    # --- Exception cases ---
    async def test_register_duplicate(self, client):
        await client.post("/api/v1/auth/register", json={
            "phone": "13800138000",
            "password": "testpass123",
        })
        resp = await client.post("/api/v1/auth/register", json={
            "phone": "13800138000",
            "password": "testpass456",
        })
        assert resp.status_code == 400

    async def test_login_wrong_password(self, client):
        await client.post("/api/v1/auth/register", json={
            "phone": "13800138000",
            "password": "testpass123",
        })
        resp = await client.post("/api/v1/auth/login", json={
            "phone": "13800138000",
            "password": "wrongpass",
        })
        assert resp.status_code == 401

    async def test_get_me_no_token(self, client):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    async def test_get_me_invalid_token(self, client):
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert resp.status_code == 401

    async def test_register_short_password(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "phone": "13800138000",
            "password": "12345",  # too short
        })
        assert resp.status_code == 422

    async def test_register_no_credentials(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "password": "testpass123",
        })
        assert resp.status_code == 400

    async def test_login_no_phone_no_email(self, client):
        resp = await client.post("/api/v1/auth/login", json={
            "password": "testpass123",
        })
        assert resp.status_code == 400
