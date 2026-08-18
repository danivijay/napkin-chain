from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.models.common import AttemptStatus
from app.schemas.progress import (
    AreaStrengthOut,
    ContinueCardOut,
    HomeOut,
    ProgressOverview,
    RecommendationOut,
    SkillsOut,
)
from app.services import (
    attempt_service,
    challenge_service,
    progress_service,
    recommendation_service,
    view_service,
)

router = APIRouter(prefix="/api/progress", tags=["progress"])


async def _overview(user_id: str) -> tuple[ProgressOverview, list, list]:
    concepts = await challenge_service.list_concepts()
    attempts = await attempt_service.latest_attempts_for_user(user_id)
    data = await progress_service.build_overview(user_id, concepts, attempts)
    overview = ProgressOverview(
        **{k: v for k, v in data.items() if k != "areas"},
        areas=[AreaStrengthOut(**a) for a in data["areas"]],
    )
    return overview, concepts, attempts


@router.get("", response_model=ProgressOverview)
async def get_progress(user: CurrentUser) -> ProgressOverview:
    overview, _, _ = await _overview(user.id)
    return overview


@router.get("/skills", response_model=SkillsOut)
async def get_skills(user: CurrentUser) -> SkillsOut:
    concepts = await challenge_service.list_concepts()
    progress = await progress_service.get_progress_map(user.id)
    return SkillsOut(
        concepts=[
            view_service.concept_summary(c, progress.get(c.concept_id)) for c in concepts
        ],
        areas=[
            AreaStrengthOut(**a)
            for a in progress_service.area_strengths(concepts, progress)
        ],
    )


@router.get("/recommendations", response_model=list[RecommendationOut])
async def get_recommendations(user: CurrentUser) -> list[RecommendationOut]:
    concepts = await challenge_service.list_concepts()
    challenges = await challenge_service.list_challenges()
    progress = await progress_service.get_progress_map(user.id)
    attempts = await attempt_service.latest_attempts_for_user(user.id)
    return [
        RecommendationOut(**r)
        for r in recommendation_service.build_recommendations(
            concepts, progress, challenges, attempts
        )
    ]


@router.get("/home", response_model=HomeOut)
async def get_home(user: CurrentUser) -> HomeOut:
    """One request backs the whole home screen."""
    overview, concepts, attempts = await _overview(user.id)
    challenges = await challenge_service.list_challenges()
    progress = await progress_service.get_progress_map(user.id)
    by_id = {c.id: c for c in challenges}

    continue_card = None
    active = next(
        (a for a in attempts if a.status is AttemptStatus.in_progress), None
    )
    if active and (challenge := by_id.get(active.challenge_id)):
        continue_card = ContinueCardOut(
            challenge_slug=challenge.slug,
            challenge_title=challenge.title,
            difficulty=challenge.difficulty,
            mode=active.mode,
            solved_count=attempt_service.solved_count(challenge, active),
            total_steps=len(challenge.estimate_nodes),
            last_activity_at=active.last_activity_at,
        )

    recommendations = [
        RecommendationOut(**r)
        for r in recommendation_service.build_recommendations(
            concepts, progress, challenges, attempts
        )
    ]
    suggested = next(
        (r.challenge_slug for r in recommendations if r.challenge_slug), None
    )
    return HomeOut(
        overview=overview,
        continue_card=continue_card,
        recommendations=recommendations,
        suggested_challenge_slug=suggested,
    )
