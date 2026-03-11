import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepository
from app.schemas.user import TokenResponse, UserCreate
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class AuthError(Exception):
    pass


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def register(self, data: UserCreate) -> User:
        if data.phone:
            existing = await self.repo.get_by_phone(data.phone)
            if existing:
                raise AuthError("Phone number already registered")
        if data.email:
            existing = await self.repo.get_by_email(data.email)
            if existing:
                raise AuthError("Email already registered")
        if not data.phone and not data.email:
            raise AuthError("Phone or email is required")

        user = await self.repo.create(
            phone=data.phone,
            email=data.email,
            nickname=data.nickname,
            password_hash=hash_password(data.password),
            role=data.role,
        )
        return user

    async def login_by_phone(self, phone: str, password: str) -> TokenResponse:
        user = await self.repo.get_by_phone(phone)
        if not user or not user.password_hash:
            raise AuthError("Invalid credentials")
        if not verify_password(password, user.password_hash):
            raise AuthError("Invalid credentials")
        return self._create_tokens(user)

    async def login_by_email(self, email: str, password: str) -> TokenResponse:
        user = await self.repo.get_by_email(email)
        if not user or not user.password_hash:
            raise AuthError("Invalid credentials")
        if not verify_password(password, user.password_hash):
            raise AuthError("Invalid credentials")
        return self._create_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthError("Invalid refresh token")
        user_id = payload.get("sub")
        if not user_id:
            raise AuthError("Invalid refresh token")
        user = await self.repo.get_by_id(uuid.UUID(user_id))
        if not user:
            raise AuthError("User not found")
        return self._create_tokens(user)

    async def get_current_user(self, token: str) -> User:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise AuthError("Invalid access token")
        user_id = payload.get("sub")
        if not user_id:
            raise AuthError("Invalid access token")
        user = await self.repo.get_by_id(uuid.UUID(user_id))
        if not user:
            raise AuthError("User not found")
        return user

    def _create_tokens(self, user: User) -> TokenResponse:
        data = {"sub": str(user.id), "role": user.role.value}
        return TokenResponse(
            access_token=create_access_token(data),
            refresh_token=create_refresh_token(data),
        )
