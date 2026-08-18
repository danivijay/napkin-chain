from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
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

    # In production the API also serves the built SPA, so the browser sees one
    # origin: the session cookie stays first-party and no CORS is involved.
    # Safari blocks third-party cookies outright, which is what a split
    # deployment across two *.onrender.com subdomains would produce.
    serve_frontend: bool = False
    frontend_dist: str = "../frontend/dist"

    #: Injected by Render at runtime. The service URL is not known until the
    #: first deploy, so deriving it beats asking someone to paste it back in.
    render_external_url: str = ""

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

    @model_validator(mode="after")
    def _adopt_platform_url(self) -> "Settings":
        """When this service serves both halves, both URLs are its own."""
        if self.serve_frontend and self.render_external_url:
            url = self.render_external_url.rstrip("/")
            self.frontend_url = url
            self.backend_url = url
        return self

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
    def same_origin(self) -> bool:
        return self.serve_frontend and self.frontend_url == self.backend_url

    @property
    def cors_origins(self) -> list[str]:
        if self.same_origin:
            return []
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
        # Lax whenever the browser sees a single origin. Only a genuinely
        # cross-site deployment needs SameSite=None, and that is a fallback,
        # not the intended setup. Either way the double-submit CSRF token in
        # core/security.py is what actually guards mutations.
        if self.is_local or self.same_origin:
            return "lax"
        return "none"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
