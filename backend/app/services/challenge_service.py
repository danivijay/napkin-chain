"""Read access to challenge and concept definitions."""

from app.db.mongodb import Collections, collection
from app.models.challenge import Challenge
from app.models.common import Difficulty
from app.models.concept import Concept

_DIFFICULTY_ORDER = {d: i for i, d in enumerate(Difficulty)}


async def list_challenges() -> list[Challenge]:
    docs = await collection(Collections.challenges).find().to_list(length=200)
    challenges = [Challenge.model_validate(d) for d in docs]
    return sorted(
        challenges,
        key=lambda c: (_DIFFICULTY_ORDER[c.difficulty], c.estimated_minutes, c.title),
    )


async def get_challenge_by_slug(slug: str) -> Challenge | None:
    doc = await collection(Collections.challenges).find_one({"slug": slug})
    return Challenge.model_validate(doc) if doc else None


async def get_challenge_by_id(challenge_id: str) -> Challenge | None:
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        oid = ObjectId(challenge_id)
    except (InvalidId, TypeError):
        return None
    doc = await collection(Collections.challenges).find_one({"_id": oid})
    return Challenge.model_validate(doc) if doc else None


async def resolve_challenge(slug_or_id: str) -> Challenge | None:
    """Routes accept a slug; internal links sometimes carry an id."""
    return await get_challenge_by_slug(slug_or_id) or await get_challenge_by_id(slug_or_id)


async def list_concepts() -> list[Concept]:
    docs = await collection(Collections.concepts).find().to_list(length=200)
    concepts = [Concept.model_validate(d) for d in docs]
    return sorted(concepts, key=lambda c: (c.area.value, c.order, c.title))


async def get_concept(concept_id: str) -> Concept | None:
    doc = await collection(Collections.concepts).find_one({"conceptId": concept_id})
    return Concept.model_validate(doc) if doc else None


async def challenges_for_concept(concept_id: str) -> list[Challenge]:
    docs = await collection(Collections.challenges).find(
        {"nodes.conceptId": concept_id}
    ).to_list(length=50)
    return [Challenge.model_validate(d) for d in docs]
