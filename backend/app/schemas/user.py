import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    phone: str | None = Field(None, pattern=r"^1[3-9]\d{9}$")
    email: str | None = None
    nickname: str = Field(default="", max_length=100)
    password: str = Field(min_length=6, max_length=128)
    role: UserRole = UserRole.CUSTOMER


class UserLogin(BaseModel):
    phone: str | None = None
    email: str | None = None
    password: str


class UserUpdate(BaseModel):
    nickname: str | None = Field(None, max_length=100)
    avatar_url: str | None = None
    email: str | None = None


class UserResponse(BaseModel):
    id: uuid.UUID
    phone: str | None
    email: str | None
    nickname: str
    avatar_url: str | None
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
