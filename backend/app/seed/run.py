"""Idempotent content seeding: ``python -m app.seed.run``.

Challenge definitions are content, not user data - re-running this updates the
definitions in place and never touches attempts or mastery.
"""

import asyncio

from app.core.logging import configure_logging, get_logger
from app.db import mongodb
from app.db.indexes import ensure_indexes
from app.db.mongodb import Collections, collection
from app.models.challenge import Challenge
from app.models.concept import Concept
from app.seed.challenges import CHALLENGES
from app.seed.concepts import CONCEPTS

logger = get_logger(__name__)


def _validated_challenges() -> list[dict]:
    documents = []
    for raw in CHALLENGES:
        # Validate before writing so a typo in content fails here, not at runtime.
        Challenge.model_validate({"_id": "seed", "schemaVersion": 1, **raw})
        documents.append({"schemaVersion": 1, **raw})
    return documents


def _validated_concepts() -> list[dict]:
    documents = []
    for raw in CONCEPTS:
        Concept.model_validate({"_id": "seed", "schemaVersion": 1, **raw})
        documents.append({"schemaVersion": 1, **raw})
    return documents


async def seed() -> dict[str, int]:
    challenges = _validated_challenges()
    concepts = _validated_concepts()

    for document in challenges:
        await collection(Collections.challenges).update_one(
            {"slug": document["slug"]}, {"$set": document}, upsert=True
        )
    for document in concepts:
        await collection(Collections.concepts).update_one(
            {"conceptId": document["conceptId"]}, {"$set": document}, upsert=True
        )

    return {"challenges": len(challenges), "concepts": len(concepts)}


async def main() -> None:
    configure_logging()
    await mongodb.connect()
    await ensure_indexes()
    counts = await seed()
    logger.info("seed.complete", extra=counts)
    print(f"Seeded {counts['challenges']} challenges and {counts['concepts']} concepts.")
    await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
