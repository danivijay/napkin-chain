from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.common import Document, utcnow


class UserPreferences(BaseModel):
    default_mode: str | None = Field(default=None, alias="defaultMode")
    reduced_motion: bool = Field(default=False, alias="reducedMotion")

    model_config = {"populate_by_name": True}


class User(Document):
    """A person. Keyed on Google's stable ``sub``; we keep nothing else from Google."""

    google_sub: str = Field(alias="googleSub")
    email: str = Field(alias="email")
    name: str | None = None
    avatar_url: str | None = Field(default=None, alias="avatarUrl")
    created_at: datetime = Field(default_factory=utcnow, alias="createdAt")
    last_login_at: datetime = Field(default_factory=utcnow, alias="lastLoginAt")
    preferences: UserPreferences = Field(default_factory=UserPreferences)


class GoogleIdentity(BaseModel):
    """The verified subset of a Google ID token we are willing to store."""

    sub: str
    email: EmailStr
    name: str | None = None
    picture: str | None = None
