from datetime import datetime

from app.schemas.common import CamelModel


class UserOut(CamelModel):
    id: str
    email: str
    name: str | None = None
    avatar_url: str | None = None
    created_at: datetime
    preferences: dict = {}


class AuthStatus(CamelModel):
    authenticated: bool
    user: UserOut | None = None
    google_enabled: bool = True
    dev_login_enabled: bool = False


class PreferencesIn(CamelModel):
    default_mode: str | None = None
    reduced_motion: bool | None = None


class DevLoginIn(CamelModel):
    email: str = "dev@napkinchain.app"
    name: str = "Dev User"
