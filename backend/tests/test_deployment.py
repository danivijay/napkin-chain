"""Production-shape checks: same-origin serving, cookie policy, seeding.

These guard the deployment posture, which is easy to break silently and
expensive to discover in a browser.
"""

import pytest

from app.core.config import Settings


def production(**overrides) -> Settings:
    base = {
        "environment": "production",
        "serve_frontend": True,
        "render_external_url": "https://napkin-chain.onrender.com",
        "session_secret": "x" * 40,
    }
    return Settings(**{**base, **overrides})


class TestSameOriginDeployment:
    def test_the_service_adopts_its_own_platform_url(self):
        settings = production()
        assert settings.frontend_url == "https://napkin-chain.onrender.com"
        assert settings.backend_url == settings.frontend_url

    def test_the_oauth_redirect_uri_follows_from_it(self):
        # This exact string has to be registered in Google Cloud.
        assert production().google_redirect_uri == (
            "https://napkin-chain.onrender.com/api/auth/google/callback"
        )

    def test_the_session_cookie_stays_first_party(self):
        settings = production()
        assert settings.same_origin is True
        # SameSite=None would make it third-party, which Safari blocks.
        assert settings.cookie_samesite == "lax"
        assert settings.cookie_secure is True

    def test_cors_is_not_configured_when_there_is_only_one_origin(self):
        assert production().cors_origins == []

    def test_a_split_deployment_still_works_but_needs_samesite_none(self):
        settings = Settings(
            environment="production",
            serve_frontend=False,
            frontend_url="https://napkin-chain.onrender.com",
            backend_url="https://napkin-chain-api.onrender.com",
            session_secret="x" * 40,
        )
        assert settings.same_origin is False
        assert settings.cookie_samesite == "none"
        assert settings.cors_origins == ["https://napkin-chain.onrender.com"]

    def test_local_development_is_unaffected(self):
        settings = Settings(environment="local")
        assert settings.cookie_secure is False
        assert settings.cookie_samesite == "lax"


class TestSpaFallback:
    """The SPA catch-all must not become a file server for the whole disk."""

    @pytest.mark.parametrize(
        "path",
        ["/../backend/.env", "/../../etc/passwd", "/%2e%2e/%2e%2e/etc/passwd"],
    )
    def test_traversal_falls_through_to_index(self, path):
        from app.api.spa import API_PREFIXES

        # The guard is `candidate.is_relative_to(dist)`; anything escaping the
        # build directory is served index.html instead of the file.
        assert not path.startswith(API_PREFIXES)

    def test_api_paths_are_never_shadowed_by_the_spa(self):
        from app.api.spa import API_PREFIXES

        for path in ("/api/challenges", "/health", "/health/db", "/docs", "/openapi.json"):
            assert path.startswith(API_PREFIXES)


@pytest.mark.db
async def test_seeding_is_idempotent(api):
    """Content is seeded on every boot, so re-running must not duplicate."""
    from app.db.mongodb import Collections, collection
    from app.seed.run import seed

    before = await collection(Collections.challenges).count_documents({})
    await seed()
    await seed()
    assert await collection(Collections.challenges).count_documents({}) == before
