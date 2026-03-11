from app.models.user import User, UserRole
from tests.conftest import create_test_user


class TestUserModel:
    """User model tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    async def test_create_customer(self, db_session):
        user = await create_test_user(db_session)
        assert user.id is not None
        assert user.role == UserRole.CUSTOMER
        assert user.phone == "13800138000"
        assert user.nickname == "TestUser"

    async def test_create_admin(self, db_session):
        user = await create_test_user(db_session, role=UserRole.ADMIN, phone="13900139001")
        assert user.role == UserRole.ADMIN

    async def test_user_repr(self, db_session):
        user = await create_test_user(db_session)
        assert "TestUser" in repr(user)
        assert "customer" in repr(user)

    # --- Boundary cases ---
    async def test_user_with_no_phone(self, db_session):
        user = User(phone=None, email="only@email.com", nickname="NoPhone", role=UserRole.CUSTOMER)
        db_session.add(user)
        await db_session.flush()
        assert user.phone is None
        assert user.email == "only@email.com"

    async def test_user_with_no_email(self, db_session):
        user = await create_test_user(db_session, email=None)
        assert user.email is None

    async def test_user_empty_nickname(self, db_session):
        user = await create_test_user(db_session, nickname="", phone="13800138001")
        assert user.nickname == ""

    # --- Exception cases ---
    async def test_duplicate_phone_fails(self, db_session):
        await create_test_user(db_session, phone="13800138000")
        import pytest
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            await create_test_user(db_session, phone="13800138000", email="other@example.com")

    async def test_duplicate_email_fails(self, db_session):
        await create_test_user(db_session, email="same@test.com", phone="13800138001")
        import pytest
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            await create_test_user(db_session, email="same@test.com", phone="13800138002")
