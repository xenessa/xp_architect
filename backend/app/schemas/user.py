"""User-related Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str
    name: str
    invite_token: str | None = None
    role: str | None = None


class UserLogin(BaseModel):
    """Schema for login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user in responses (no password)."""

    id: UUID
    email: str
    name: str
    role: UserRole
    assessment_completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenWithUser(BaseModel):
    """Schema for login response: token and user."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
