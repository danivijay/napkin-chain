from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser
from app.models.challenge import Challenge
from app.schemas.challenge import ChallengeDetail, ChallengeSummary
from app.services import attempt_service, challenge_service, progress_service, view_service

router = APIRouter(prefix="/api/challenges", tags=["challenges"])


async def resolve_or_404(slug: str) -> Challenge:
    challenge = await challenge_service.resolve_challenge(slug)
    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found"
        )
    return challenge


@router.get("", response_model=list[ChallengeSummary])
async def list_challenges(user: CurrentUser) -> list[ChallengeSummary]:
    challenges = await challenge_service.list_challenges()
    attempts = await attempt_service.latest_attempts_for_user(user.id)
    latest = {}
    for attempt in attempts:  # already sorted by lastActivityAt desc
        latest.setdefault(attempt.challenge_id, attempt)
    return [
        view_service.challenge_summary(c, latest.get(c.id)) for c in challenges
    ]


@router.get("/{slug}", response_model=ChallengeDetail)
async def get_challenge(slug: str, user: CurrentUser) -> ChallengeDetail:
    challenge = await resolve_or_404(slug)
    attempt = await attempt_service.get_latest_attempt(user.id, challenge.id)
    all_concepts = await challenge_service.list_concepts()
    by_id = {c.concept_id: c for c in all_concepts}
    concepts = [by_id[cid] for cid in challenge.concept_ids if cid in by_id]
    progress = await progress_service.get_progress_map(user.id)
    return view_service.challenge_detail(challenge, attempt, concepts, progress)
