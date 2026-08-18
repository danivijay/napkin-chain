"""Building the chain: start, answer, hint, retry, resume, result."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.challenges import resolve_or_404
from app.api.deps import CurrentUser, CsrfProtected, submit_rate_limit
from app.models.attempt import ChallengeAttempt
from app.models.challenge import Challenge
from app.models.common import AttemptStatus, Mode, NodeStatus
from app.models.event import EventName
from app.schemas.attempt import (
    AttemptStateOut,
    ChallengeResultOut,
    EstimateIn,
    EstimateOut,
    HintOut,
    StartAttemptIn,
)
from app.schemas.challenge import NodeQuestion
from app.services import (
    analytics_service,
    attempt_service,
    challenge_service,
    progress_service,
    view_service,
)
from app.services.attempt_service import AttemptError

router = APIRouter(prefix="/api/challenges", tags=["attempts"])


async def _concept_titles() -> dict[str, str]:
    concepts = await challenge_service.list_concepts()
    return {c.concept_id: c.title for c in concepts}


async def _load_attempt(user_id: str, challenge: Challenge) -> ChallengeAttempt:
    attempt = await attempt_service.get_active_attempt(user_id, challenge.id)
    if attempt is None:
        attempt = await attempt_service.get_latest_attempt(user_id, challenge.id)
    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No attempt in progress"
        )
    return attempt


async def _state(challenge: Challenge, attempt: ChallengeAttempt) -> AttemptStateOut:
    return view_service.attempt_state_out(challenge, attempt, await _concept_titles())


@router.post("/{slug}/attempts", response_model=AttemptStateOut)
async def start_attempt(
    slug: str, payload: StartAttemptIn, user: CurrentUser, _: CsrfProtected = None
) -> AttemptStateOut:
    challenge = await resolve_or_404(slug)
    if payload.mode not in challenge.modes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This challenge does not support that mode",
        )

    attempt, created = await attempt_service.start_or_resume(
        user.id, challenge, payload.mode, restart=payload.restart
    )
    await analytics_service.track(
        EventName.challenge_started
        if created
        else EventName.challenge_resumed,
        user_id=user.id,
        challengeSlug=challenge.slug,
        mode=payload.mode.value,
        restart=payload.restart,
    )
    return await _state(challenge, attempt)


@router.get("/{slug}/progress", response_model=AttemptStateOut)
async def get_progress(slug: str, user: CurrentUser) -> AttemptStateOut:
    challenge = await resolve_or_404(slug)
    attempt = await _load_attempt(user.id, challenge)
    return await _state(challenge, attempt)


@router.post("/{slug}/resume", response_model=AttemptStateOut)
async def resume(slug: str, user: CurrentUser, _: CsrfProtected = None) -> AttemptStateOut:
    challenge = await resolve_or_404(slug)
    attempt = await _load_attempt(user.id, challenge)
    if attempt.status is AttemptStatus.abandoned:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="That attempt was abandoned"
        )
    attempt, _created = await attempt_service.start_or_resume(
        user.id, challenge, attempt.mode
    )
    await analytics_service.track(
        EventName.challenge_resumed, user_id=user.id, challengeSlug=challenge.slug
    )
    return await _state(challenge, attempt)


@router.get("/{slug}/nodes/{node_id}", response_model=NodeQuestion)
async def get_node(slug: str, node_id: str, user: CurrentUser) -> NodeQuestion:
    challenge = await resolve_or_404(slug)
    attempt = await _load_attempt(user.id, challenge)
    node = challenge.node(node_id)
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown step")

    progress = attempt.nodes.get(node_id)
    if progress is None or progress.status is NodeStatus.locked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="This step is still locked"
        )
    return view_service.question_out(challenge, node, progress, await _concept_titles())


@router.post(
    "/{slug}/nodes/{node_id}/estimate",
    response_model=EstimateOut,
    dependencies=[Depends(submit_rate_limit)],
)
async def submit_estimate(
    slug: str,
    node_id: str,
    payload: EstimateIn,
    user: CurrentUser,
    _: CsrfProtected = None,
) -> EstimateOut:
    challenge = await resolve_or_404(slug)
    attempt = await _load_attempt(user.id, challenge)

    try:
        result = await attempt_service.submit_estimate(
            user_id=user.id,
            challenge=challenge,
            attempt=attempt,
            node_id=node_id,
            estimate=payload.estimate,
            calculation=payload.calculation,
            seconds=payload.time_spent_seconds,
            used_hint=payload.used_hint,
        )
    except AttemptError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc

    if result.node.concept_id:
        await progress_service.record_estimate(
            user.id,
            result.node.concept_id,
            classification=result.evaluation.classification,
            ratio=result.evaluation.ratio,
            passed=result.evaluation.passed,
            attempt_number=result.attempt_number,
            used_hint=result.used_hint,
            seconds=result.seconds,
            difficulty=challenge.difficulty,
        )

    await analytics_service.track(
        EventName.node_solved if result.evaluation.passed else EventName.node_attempted,
        user_id=user.id,
        challengeSlug=challenge.slug,
        nodeId=node_id,
        classification=result.evaluation.classification.value,
        ratio=result.evaluation.ratio,
        attemptNumber=result.attempt_number,
    )
    if result.completed:
        await analytics_service.track(
            EventName.challenge_completed,
            user_id=user.id,
            challengeSlug=challenge.slug,
            score=result.attempt.score,
            mode=result.attempt.mode.value,
        )

    concept_titles = await _concept_titles()
    return EstimateOut(
        feedback=view_service.feedback_out(
            result.node, result.evaluation, result.node_status, concept_titles
        ),
        state=view_service.attempt_state_out(challenge, result.attempt, concept_titles),
        unlocked_node_ids=result.unlocked_node_ids,
        challenge_completed=result.completed,
    )


@router.post("/{slug}/nodes/{node_id}/retry", response_model=AttemptStateOut)
async def retry_node(
    slug: str, node_id: str, user: CurrentUser, _: CsrfProtected = None
) -> AttemptStateOut:
    challenge = await resolve_or_404(slug)
    attempt = await _load_attempt(user.id, challenge)
    try:
        attempt = await attempt_service.retry_node(challenge, attempt, node_id)
    except AttemptError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc

    await analytics_service.track(
        EventName.node_retried,
        user_id=user.id,
        challengeSlug=challenge.slug,
        nodeId=node_id,
    )
    return await _state(challenge, attempt)


@router.post("/{slug}/nodes/{node_id}/hint", response_model=HintOut)
async def hint(
    slug: str, node_id: str, user: CurrentUser, _: CsrfProtected = None
) -> HintOut:
    challenge = await resolve_or_404(slug)
    attempt = await _load_attempt(user.id, challenge)
    if attempt.mode is Mode.interview:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hints are not available in interview mode",
        )
    try:
        text, revealed, available = await attempt_service.reveal_hint(
            challenge, attempt, node_id
        )
    except AttemptError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc

    await analytics_service.track(
        EventName.hint_used,
        user_id=user.id,
        challengeSlug=challenge.slug,
        nodeId=node_id,
    )
    return HintOut(hint=text, hints_revealed=revealed, hints_available=available)


@router.post("/{slug}/nodes/{node_id}/draft", status_code=status.HTTP_204_NO_CONTENT)
async def save_draft(
    slug: str,
    node_id: str,
    payload: dict,
    user: CurrentUser,
    _: CsrfProtected = None,
) -> None:
    """Persist rough work so a refresh or a dropped connection never loses it."""
    challenge = await resolve_or_404(slug)
    attempt = await _load_attempt(user.id, challenge)
    calculation = payload.get("calculation")
    if calculation is not None and not isinstance(calculation, str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="calculation must be text",
        )
    await attempt_service.save_calculation_draft(
        attempt, node_id, (calculation or "")[:2000] or None
    )


@router.get("/{slug}/result", response_model=ChallengeResultOut)
async def get_result(slug: str, user: CurrentUser) -> ChallengeResultOut:
    challenge = await resolve_or_404(slug)
    attempt = await _load_attempt(user.id, challenge)
    return view_service.challenge_result(challenge, attempt)
