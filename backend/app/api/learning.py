from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, CsrfProtected
from app.models.event import EventName
from app.schemas.concept import ConceptDetail, ConceptGroupOut, DrillIn, DrillOut
from app.services import (
    analytics_service,
    challenge_service,
    progress_service,
    view_service,
)
from app.services.evaluation_service import evaluate_estimate
from app.models.challenge import ChallengeNode, Thresholds
from app.models.common import Difficulty, NodeType
from app.services.progress_service import AREA_TITLES

router = APIRouter(prefix="/api/concepts", tags=["learning"])


@router.get("", response_model=list[ConceptGroupOut])
async def list_concepts(user: CurrentUser) -> list[ConceptGroupOut]:
    concepts = await challenge_service.list_concepts()
    progress = await progress_service.get_progress_map(user.id)

    grouped: dict[str, list] = {}
    for concept in concepts:
        grouped.setdefault(concept.area.value, []).append(
            view_service.concept_summary(concept, progress.get(concept.concept_id))
        )
    return [
        ConceptGroupOut(area=area.value, title=title, concepts=grouped[area.value])
        for area, title in AREA_TITLES.items()
        if area.value in grouped
    ]


@router.get("/{concept_id}", response_model=ConceptDetail)
async def get_concept(concept_id: str, user: CurrentUser) -> ConceptDetail:
    concept = await challenge_service.get_concept(concept_id)
    if concept is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found"
        )

    all_concepts = await challenge_service.list_concepts()
    related = [c for c in all_concepts if c.concept_id in concept.related_concept_ids]
    challenges = await challenge_service.challenges_for_concept(concept_id)
    progress_map = await progress_service.get_progress_map(user.id)

    await analytics_service.track(
        EventName.concept_viewed, user_id=user.id, conceptId=concept_id
    )
    return view_service.concept_detail(
        concept, progress_map.get(concept_id), related, challenges, progress_map
    )


@router.post("/{concept_id}/learned", response_model=ConceptDetail)
async def mark_learned(
    concept_id: str, user: CurrentUser, _: CsrfProtected = None
) -> ConceptDetail:
    concept = await challenge_service.get_concept(concept_id)
    if concept is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found"
        )
    await progress_service.mark_learned(user.id, concept_id)
    await analytics_service.track(
        EventName.concept_learned, user_id=user.id, conceptId=concept_id
    )
    return await get_concept(concept_id, user)


@router.post("/{concept_id}/practice", response_model=DrillOut)
async def practice(
    concept_id: str, payload: DrillIn, user: CurrentUser, _: CsrfProtected = None
) -> DrillOut:
    """The 'Try it' drill at the end of a concept, scored like any estimate."""
    concept = await challenge_service.get_concept(concept_id)
    if concept is None or concept.drill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No drill for this concept"
        )
    if payload.estimate <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Estimate must be greater than zero",
        )

    node = ChallengeNode(
        id=f"drill:{concept_id}",
        type=NodeType.estimate,
        label=concept.title,
        unit=concept.drill.unit,
        expectedMin=concept.drill.expected_min,
        expectedMax=concept.drill.expected_max,
    )
    evaluation = evaluate_estimate(node, payload.estimate, Thresholds())

    progress = await progress_service.record_estimate(
        user.id,
        concept_id,
        classification=evaluation.classification,
        ratio=evaluation.ratio,
        passed=evaluation.passed,
        attempt_number=1,
        used_hint=False,
        seconds=payload.time_spent_seconds,
        difficulty=Difficulty.foundation,
    )
    await analytics_service.track(
        EventName.concept_practiced,
        user_id=user.id,
        conceptId=concept_id,
        classification=evaluation.classification.value,
    )

    return DrillOut(
        passed=evaluation.passed,
        ratio=evaluation.ratio,
        classification=evaluation.classification.value,
        headline=evaluation.headline,
        expected_min=concept.drill.expected_min,
        expected_max=concept.drill.expected_max,
        explanation=concept.drill.explanation,
        mastery=progress.mastery,
        status=progress.status.value,
    )
