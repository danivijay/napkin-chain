from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration. Every value comes from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    environment: Literal["local", "staging", "production"] = "local"

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "napkin_chain"

    google_client_id: str = ""
    google_client_secret: str = ""

    session_secret: str = "dev-only-insecure-secret-change-me"
    session_ttl_seconds: int = 60 * 60 * 24 * 14  # 14 days

    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"

    # Comma-separated list of extra allowed CORS origins.
    extra_cors_origins: str = ""

    log_level: str = "INFO"

    # Rate limits (requests per window, window in seconds).
    auth_rate_limit: int = Field(default=20)
    auth_rate_window_seconds: int = Field(default=60)
    submit_rate_limit: int = Field(default=120)
    submit_rate_window_seconds: int = Field(default=60)

    @field_validator("frontend_url", "backend_url")
    @classmethod
    def _strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_local(self) -> bool:
        return self.environment == "local"

    @property
    def google_configured(self) -> bool:
        return bool(self.google_client_id and self.google_client_secret)

    @property
    def google_redirect_uri(self) -> str:
        return f"{self.backend_url}/api/auth/google/callback"

    @property
    def cors_origins(self) -> list[str]:
        origins = {self.frontend_url}
        origins.update(
            o.strip().rstrip("/") for o in self.extra_cors_origins.split(",") if o.strip()
        )
        return sorted(origins)

    @property
    def cookie_secure(self) -> bool:
        return not self.is_local

    @property
    def cookie_samesite(self) -> Literal["lax", "none"]:
        # The deployed frontend and API live on different sites (Render gives
        # each service its own subdomain of a public-suffix domain), so the
        # session cookie has to be SameSite=None there. CSRF is handled by the
        # double-submit token in core/security.py.
        return "lax" if self.is_local else "none"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
