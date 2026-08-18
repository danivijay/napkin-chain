from typing import Any

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect(uri: str | None = None, db_name: str | None = None) -> AsyncIOMotorDatabase:
    global _client, _db
    _client = AsyncIOMotorClient(
        uri or settings.mongodb_uri,
        serverSelectionTimeoutMS=8000,
        uuidRepresentation="standard",
        # Without this, datetimes come back naive and every client has to
        # guess that they are UTC. They then guess wrong.
        tz_aware=True,
    )
    _db = _client[db_name or settings.mongodb_db]
    logger.info("mongodb.connected", extra={"database": _db.name})
    return _db


async def disconnect() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
    _client, _db = None, None


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("MongoDB is not connected; call connect() during startup")
    return _db


async def ping() -> dict[str, Any]:
    """Health probe for the database, reported separately from the API's own health."""
    if _client is None:
        return {"status": "disconnected"}
    try:
        await _client.admin.command("ping")
    except Exception as exc:  # noqa: BLE001 - surfaced as degraded, never raised
        logger.warning("mongodb.ping_failed", extra={"error": str(exc)})
        return {"status": "error"}
    return {"status": "ok"}


class Collections:
    users = "users"
    challenges = "challenges"
    concepts = "concepts"
    challenge_attempts = "challenge_attempts"
    node_attempts = "node_attempts"
    concept_progress = "concept_progress"
    events = "events"


def collection(name: str) -> AsyncIOMotorCollection:
    return get_db()[name]
