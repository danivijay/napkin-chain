"""Minimal in-house product analytics: append-only event documents."""

from typing import Any

from app.core.logging import get_logger
from app.db.mongodb import Collections, collection
from app.models.common import utcnow
from app.models.event import EventName

logger = get_logger(__name__)


async def track(
    name: EventName, user_id: str | None = None, **properties: Any
) -> None:
    """Fire-and-forget. Analytics must never break a user action."""
    try:
        await collection(Collections.events).insert_one(
            {
                "schemaVersion": 1,
                "userId": user_id,
                "name": name.value,
                "properties": properties,
                "createdAt": utcnow(),
            }
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("analytics.write_failed", extra={"event": name.value, "error": str(exc)})
