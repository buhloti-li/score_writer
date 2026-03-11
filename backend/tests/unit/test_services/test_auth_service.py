import pytest

from app.schemas.user import UserCreate
from app.services.auth_service import AuthError, AuthService


class TestAuthService:
    """Auth service tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    async def test_register_with_phone(self, db_session):
        service = AuthService(db_session)
        user = await service.register(
            UserCreate(phone="13800138000", password="testpass123", nickname="Test")
        )
        assert user.phone == "13800138000"
        assert user.nickname == "Test"

    async def test_register_with_email(self, db_session):
        service = AuthService(db_session)
        user = await service.register(
            UserCreate(email="test@test.com", password="testpass123")
        )
        assert user.email == "test@test.com"

    async def test_login_by_phone(self, db_session):
        service = AuthService(db_session)
        await service.register(
            UserCreate(phone="13800138000", password="testpass123")
        )
        tokens = await service.login_by_phone("13800138000", "testpass123")
        assert tokens.access_token
        assert tokens.refresh_token
        assert tokens.token_type == "bearer"

    async def test_login_by_email(self, db_session):
        service = AuthService(db_session)
        await service.register(
            UserCreate(email="test@test.com", password="testpass123")
        )
        tokens = await service.login_by_email("test@test.com", "testpass123")
        assert tokens.access_token

    async def test_get_current_user(self, db_session):
        service = AuthService(db_session)
        user = await service.register(
            UserCreate(phone="13800138000", password="testpass123")
        )
        tokens = await service.login_by_phone("13800138000", "testpass123")
        current = await service.get_current_user(tokens.access_token)
        assert current.id == user.id

    async def test_refresh_token(self, db_session):
        service = AuthService(db_session)
        await service.register(
            UserCreate(phone="13800138000", password="testpass123")
        )
        tokens = await service.login_by_phone("13800138000", "testpass123")
        new_tokens = await service.refresh(tokens.refresh_token)
        assert new_tokens.access_token
        assert new_tokens.refresh_token
        assert new_tokens.token_type == "bearer"
        # Verify new access token is valid by decoding it
        from app.utils.security import decode_token
        payload = decode_token(new_tokens.access_token)
        assert payload["type"] == "access"

    # --- Boundary cases ---
    async def test_register_with_both_phone_and_email(self, db_session):
        service = AuthService(db_session)
        user = await service.register(
            UserCreate(phone="13800138000", email="both@test.com", password="testpass123")
        )
        assert user.phone == "13800138000"
        assert user.email == "both@test.com"

    # --- Exception cases ---
    async def test_register_duplicate_phone(self, db_session):
        service = AuthService(db_session)
        await service.register(
            UserCreate(phone="13800138000", password="testpass123")
        )
        with pytest.raises(AuthError, match="Phone number already registered"):
            await service.register(
                UserCreate(phone="13800138000", password="testpass456")
            )

    async def test_register_duplicate_email(self, db_session):
        service = AuthService(db_session)
        await service.register(
            UserCreate(email="dup@test.com", password="testpass123")
        )
        with pytest.raises(AuthError, match="Email already registered"):
            await service.register(
                UserCreate(email="dup@test.com", password="testpass456")
            )

    async def test_register_no_phone_no_email(self, db_session):
        service = AuthService(db_session)
        with pytest.raises(AuthError, match="Phone or email is required"):
            await service.register(UserCreate(password="testpass123"))

    async def test_login_wrong_password(self, db_session):
        service = AuthService(db_session)
        await service.register(
            UserCreate(phone="13800138000", password="testpass123")
        )
        with pytest.raises(AuthError, match="Invalid credentials"):
            await service.login_by_phone("13800138000", "wrongpass")

    async def test_login_nonexistent_user(self, db_session):
        service = AuthService(db_session)
        with pytest.raises(AuthError, match="Invalid credentials"):
            await service.login_by_phone("19999999999", "testpass123")

    async def test_get_current_user_invalid_token(self, db_session):
        service = AuthService(db_session)
        with pytest.raises(AuthError, match="Invalid access token"):
            await service.get_current_user("invalid-token-string")

    async def test_refresh_with_access_token_fails(self, db_session):
        service = AuthService(db_session)
        await service.register(
            UserCreate(phone="13800138000", password="testpass123")
        )
        tokens = await service.login_by_phone("13800138000", "testpass123")
        with pytest.raises(AuthError, match="Invalid refresh token"):
            await service.refresh(tokens.access_token)  # access token, not refresh
