from pymongo import ASCENDING, DESCENDING, IndexModel

from app.core.logging import get_logger
from app.db.mongodb import Collections, get_db

logger = get_logger(__name__)

_INDEXES: dict[str, list[IndexModel]] = {
    Collections.users: [
        IndexModel([("googleSub", ASCENDING)], unique=True, name="googleSub_unique"),
        IndexModel([("email", ASCENDING)], name="email"),
    ],
    Collections.challenges: [
        IndexModel([("slug", ASCENDING)], unique=True, name="slug_unique"),
        IndexModel([("difficulty", ASCENDING)], name="difficulty"),
    ],
    Collections.concepts: [
        IndexModel([("conceptId", ASCENDING)], unique=True, name="conceptId_unique"),
        IndexModel([("area", ASCENDING), ("order", ASCENDING)], name="area_order"),
    ],
    Collections.challenge_attempts: [
        IndexModel(
            [("userId", ASCENDING), ("challengeId", ASCENDING)],
            name="user_challenge",
        ),
        IndexModel(
            [("userId", ASCENDING), ("lastActivityAt", DESCENDING)],
            name="user_recent",
        ),
    ],
    Collections.node_attempts: [
        IndexModel(
            [("userId", ASCENDING), ("challengeId", ASCENDING), ("nodeId", ASCENDING)],
            name="user_challenge_node",
        ),
        IndexModel([("userId", ASCENDING), ("createdAt", DESCENDING)], name="user_recent"),
    ],
    Collections.concept_progress: [
        IndexModel(
            [("userId", ASCENDING), ("conceptId", ASCENDING)],
            unique=True,
            name="user_concept_unique",
        ),
    ],
    Collections.events: [
        IndexModel([("userId", ASCENDING), ("createdAt", DESCENDING)], name="user_recent"),
    ],
}


async def ensure_indexes() -> None:
    db = get_db()
    for name, indexes in _INDEXES.items():
        await db[name].create_indexes(indexes)
    logger.info("mongodb.indexes_ready", extra={"collections": list(_INDEXES)})
