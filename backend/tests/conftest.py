"""Test fixtures.

Database-backed tests run against a dedicated test database on whatever
MONGODB_URI is configured; they are skipped when no database is reachable, so
the pure evaluation and mastery suites always run.
"""

import os

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("ENVIRONMENT", "local")
os.environ.setdefault("LOG_LEVEL", "CRITICAL")
os.environ["MONGODB_DB"] = os.environ.get("MONGODB_TEST_DB", "napkin_chain_test")

from app.core.config import get_settings  # noqa: E402

get_settings.cache_clear()

from app.core.security import CSRF_COOKIE, CSRF_HEADER, auth_rate_limiter, submit_rate_limiter  # noqa: E402
from app.db import mongodb  # noqa: E402
from app.main import app  # noqa: E402
from app.seed.run import seed  # noqa: E402


@pytest_asyncio.fixture(scope="session")
async def api():
    auth_rate_limiter.reset()
    submit_rate_limiter.reset()
    try:
        async with LifespanManager(app, startup_timeout=20):
            await mongodb.ping()
            await seed()
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                yield client
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"database unavailable: {exc}")


class Session:
    """A signed-in client that carries the CSRF token like the SPA does."""

    def __init__(self, client: AsyncClient, user_id: str) -> None:
        self.client = client
        self.user_id = user_id

    def _headers(self) -> dict[str, str]:
        token = self.client.cookies.get(CSRF_COOKIE, "")
        return {CSRF_HEADER: token}

    async def get(self, url: str, **kwargs):
        return await self.client.get(url, **kwargs)

    async def post(self, url: str, **kwargs):
        headers = {**self._headers(), **kwargs.pop("headers", {})}
        return await self.client.post(url, headers=headers, **kwargs)

    async def delete(self, url: str, **kwargs):
        headers = {**self._headers(), **kwargs.pop("headers", {})}
        return await self.client.delete(url, headers=headers, **kwargs)


async def sign_in(client: AsyncClient, email: str) -> Session:
    auth_rate_limiter.reset()
    response = await client.post(
        "/api/auth/dev-login", json={"email": email, "name": "Test User"}
    )
    assert response.status_code == 200, response.text
    return Session(client, response.json()["user"]["id"])


@pytest_asyncio.fixture
async def session(api: AsyncClient):
    api.cookies.clear()
    session = await sign_in(api, "primary@napkinchain.app")
    await session.delete("/api/users/me/progress")
    yield session
    api.cookies.clear()
