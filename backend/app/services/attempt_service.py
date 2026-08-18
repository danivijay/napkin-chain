"""The chain state machine: starting, resuming, answering and completing.

This module owns everything about *what the user did*. It never mutates a
challenge definition and never writes mastery - it hands facts to
mastery_service and lets that decide what the user knows.
"""

from dataclasses import dataclass
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId

from app.db.mongodb import Collections, collection
from app.models.attempt import ChallengeAttempt, NodeProgress
from app.models.challenge import Challenge, ChallengeNode
from app.models.common import (
    AttemptStatus,
    Mode,
    NodeStatus,
    NodeType,
    utcnow,
)
from app.services import evaluation_service
from app.services.evaluation_service import Evaluation
from app.services.formatting import humanize

RESOLVED_STATUSES = {NodeStatus.solved, NodeStatus.weak, NodeStatus.mastered}


class AttemptError(Exception):
    """A request that does not make sense for the current chain state."""


@dataclass(frozen=True)
class SubmissionResult:
    attempt: ChallengeAttempt
    evaluation: Evaluation
    node: ChallengeNode
    node_status: NodeStatus
    attempt_number: int
    unlocked_node_ids: list[str]
    completed: bool
    used_hint: bool
    seconds: int


# --------------------------------------------------------------------------
# Chain topology
# --------------------------------------------------------------------------


def initial_nodes(challenge: Challenge) -> dict[str, NodeProgress]:
    """Input nodes start solved - they are givens, not questions."""
    nodes: dict[str, NodeProgress] = {}
    for node in challenge.nodes:
        if node.type is NodeType.input:
            nodes[node.id] = NodeProgress(status=NodeStatus.solved, solved_at=utcnow())
        else:
            nodes[node.id] = NodeProgress(status=NodeStatus.locked)
    recompute_availability(challenge, nodes)
    return nodes


def recompute_availability(
    challenge: Challenge, nodes: dict[str, NodeProgress]
) -> str | None:
    """Unlock every node whose dependencies are resolved; return the active node."""
    for node in challenge.nodes:
        progress = nodes.setdefault(node.id, NodeProgress())
        if progress.status in RESOLVED_STATUSES:
            continue
        deps_ready = all(
            nodes.get(dep, NodeProgress()).status in RESOLVED_STATUSES
            for dep in node.depends_on
        )
        progress.status = NodeStatus.available if deps_ready else NodeStatus.locked

    current = next(
        (
            node.id
            for node in challenge.nodes
            if node.type is NodeType.estimate
            and nodes[node.id].status is NodeStatus.available
        ),
        None,
    )
    if current:
        nodes[current].status = NodeStatus.active
    return current


def unlocked_by(
    challenge: Challenge, nodes: dict[str, NodeProgress], solved_node_id: str
) -> list[str]:
    """Nodes that became answerable because ``solved_node_id`` was answered."""
    return [
        node.id
        for node in challenge.nodes
        if solved_node_id in node.depends_on
        and nodes[node.id].status in {NodeStatus.available, NodeStatus.active}
    ]


def is_complete(challenge: Challenge, nodes: dict[str, NodeProgress]) -> bool:
    return all(
        nodes.get(node.id, NodeProgress()).status in RESOLVED_STATUSES
        for node in challenge.estimate_nodes
    )


def display_value(
    challenge: Challenge, node: ChallengeNode, progress: NodeProgress
) -> str | None:
    """What the node shows on the napkin: the given, or the user's own number."""
    if node.type is NodeType.input:
        return node.display_value or humanize(node.value or 0, node.unit)
    if progress.status in RESOLVED_STATUSES and progress.last_estimate is not None:
        return humanize(progress.last_estimate, node.unit)
    return None


# --------------------------------------------------------------------------
# Persistence
# --------------------------------------------------------------------------


def _oid(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError) as exc:
        raise AttemptError("invalid identifier") from exc


def _to_document(attempt: ChallengeAttempt) -> dict:
    doc = attempt.model_dump(by_alias=True, exclude={"id"})
    doc["nodes"] = {
        node_id: progress.model_dump(by_alias=True)
        for node_id, progress in attempt.nodes.items()
    }
    return doc


async def _save(attempt: ChallengeAttempt) -> None:
    await collection(Collections.challenge_attempts).update_one(
        {"_id": _oid(attempt.id)}, {"$set": _to_document(attempt)}
    )


async def get_active_attempt(user_id: str, challenge_id: str) -> ChallengeAttempt | None:
    doc = await collection(Collections.challenge_attempts).find_one(
        {
            "userId": user_id,
            "challengeId": challenge_id,
            "status": AttemptStatus.in_progress.value,
        },
        sort=[("lastActivityAt", -1)],
    )
    return ChallengeAttempt.model_validate(doc) if doc else None


async def get_latest_attempt(user_id: str, challenge_id: str) -> ChallengeAttempt | None:
    doc = await collection(Collections.challenge_attempts).find_one(
        {"userId": user_id, "challengeId": challenge_id},
        sort=[("lastActivityAt", -1)],
    )
    return ChallengeAttempt.model_validate(doc) if doc else None


async def get_attempt_by_id(user_id: str, attempt_id: str) -> ChallengeAttempt | None:
    """Authorization lives in the query: a user can only load their own attempt."""
    doc = await collection(Collections.challenge_attempts).find_one(
        {"_id": _oid(attempt_id), "userId": user_id}
    )
    return ChallengeAttempt.model_validate(doc) if doc else None


async def latest_attempts_for_user(
    user_id: str, limit: int = 50
) -> list[ChallengeAttempt]:
    docs = await (
        collection(Collections.challenge_attempts)
        .find({"userId": user_id})
        .sort("lastActivityAt", -1)
        .to_list(length=limit)
    )
    return [ChallengeAttempt.model_validate(d) for d in docs]


async def start_or_resume(
    user_id: str, challenge: Challenge, mode: Mode, restart: bool = False
) -> tuple[ChallengeAttempt, bool]:
    """Returns ``(attempt, created)``. Resuming never loses the user's place."""
    existing = await get_active_attempt(user_id, challenge.id)

    if existing and not restart:
        if existing.mode != mode:
            existing.mode = mode
        existing.current_node_id = recompute_availability(challenge, existing.nodes)
        existing.last_activity_at = utcnow()
        await _save(existing)
        return existing, False

    if existing and restart:
        existing.status = AttemptStatus.abandoned
        await _save(existing)

    nodes = initial_nodes(challenge)
    attempt = ChallengeAttempt(
        _id=str(ObjectId()),
        userId=user_id,
        challengeId=challenge.id,
        challengeSlug=challenge.slug,
        mode=mode,
        nodes=nodes,
        currentNodeId=recompute_availability(challenge, nodes),
    )
    document = _to_document(attempt)
    document["_id"] = _oid(attempt.id)
    document["schemaVersion"] = 1
    await collection(Collections.challenge_attempts).insert_one(document)
    return attempt, True


# --------------------------------------------------------------------------
# Answering
# --------------------------------------------------------------------------


def _require_answerable(
    challenge: Challenge, attempt: ChallengeAttempt, node_id: str
) -> ChallengeNode:
    node = challenge.node(node_id)
    if node is None:
        raise AttemptError("unknown node")
    if node.type is NodeType.input:
        raise AttemptError("input nodes are given, not estimated")
    progress = attempt.nodes.get(node_id, NodeProgress())
    if progress.status is NodeStatus.locked:
        raise AttemptError("this step is still locked")
    return node


async def submit_estimate(
    user_id: str,
    challenge: Challenge,
    attempt: ChallengeAttempt,
    node_id: str,
    estimate: float,
    calculation: str | None,
    seconds: int,
    used_hint: bool,
) -> SubmissionResult:
    node = _require_answerable(challenge, attempt, node_id)
    progress = attempt.nodes[node_id]

    evaluation = evaluation_service.evaluate_node(challenge, node, estimate)
    attempt_number = progress.attempts + 1
    hint_used = used_hint or progress.used_hint or progress.hints_revealed > 0
    status = evaluation_service.node_status_for(
        evaluation, attempt_number=attempt_number, used_hint=hint_used
    )

    progress.attempts = attempt_number
    progress.status = status
    progress.last_estimate = estimate
    progress.last_calculation = calculation
    progress.last_ratio = evaluation.ratio
    progress.best_ratio = (
        evaluation.ratio
        if progress.best_ratio is None
        else min(progress.best_ratio, evaluation.ratio)
    )
    progress.classification = evaluation.classification
    progress.used_hint = hint_used
    progress.time_spent_seconds += seconds
    progress.solved_at = utcnow()

    now = utcnow()
    attempt.time_spent_seconds += seconds
    attempt.last_activity_at = now
    attempt.current_node_id = recompute_availability(challenge, attempt.nodes)
    unlocked = unlocked_by(challenge, attempt.nodes, node_id)

    completed = is_complete(challenge, attempt.nodes)
    if completed and attempt.status is AttemptStatus.in_progress:
        attempt.status = AttemptStatus.completed
        attempt.completed_at = now
        attempt.current_node_id = None
        ratios = [
            p.last_ratio
            for n in challenge.estimate_nodes
            if (p := attempt.nodes.get(n.id)) and p.last_ratio is not None
        ]
        attempt.average_ratio = round(sum(ratios) / len(ratios), 3) if ratios else None
        attempt.score = _score_from_progress(challenge, attempt)

    await _save(attempt)
    await _record_node_attempt(
        user_id=user_id,
        challenge=challenge,
        attempt=attempt,
        node=node,
        evaluation=evaluation,
        attempt_number=attempt_number,
        seconds=seconds,
        used_hint=hint_used,
        calculation=calculation,
    )

    return SubmissionResult(
        attempt=attempt,
        evaluation=evaluation,
        node=node,
        node_status=status,
        attempt_number=attempt_number,
        unlocked_node_ids=unlocked,
        completed=completed,
        used_hint=hint_used,
        seconds=seconds,
    )


def _score_from_progress(challenge: Challenge, attempt: ChallengeAttempt) -> float:
    quality = {
        "excellent": 1.0,
        "very_good": 0.85,
        "good": 0.65,
        "developing": 0.35,
        "needs_review": 0.1,
    }
    scores = [
        quality.get(p.classification.value, 0.0)
        for n in challenge.estimate_nodes
        if (p := attempt.nodes.get(n.id)) and p.classification
    ]
    return round(sum(scores) / len(scores), 3) if scores else 0.0


async def _record_node_attempt(
    *,
    user_id: str,
    challenge: Challenge,
    attempt: ChallengeAttempt,
    node: ChallengeNode,
    evaluation: Evaluation,
    attempt_number: int,
    seconds: int,
    used_hint: bool,
    calculation: str | None,
) -> None:
    await collection(Collections.node_attempts).insert_one(
        {
            "schemaVersion": 1,
            "userId": user_id,
            "challengeId": challenge.id,
            "challengeAttemptId": attempt.id,
            "nodeId": node.id,
            "conceptId": node.concept_id,
            "mode": attempt.mode.value,
            "attemptNumber": attempt_number,
            "estimate": evaluation.estimate,
            "expectedValue": evaluation.target,
            "expectedMin": evaluation.expected_min,
            "expectedMax": evaluation.expected_max,
            "ratio": evaluation.ratio,
            "classification": evaluation.classification.value,
            "timeSpentSeconds": seconds,
            "usedHint": used_hint,
            "calculation": calculation,
            "createdAt": utcnow(),
        }
    )


async def retry_node(
    challenge: Challenge, attempt: ChallengeAttempt, node_id: str
) -> ChallengeAttempt:
    """Reopen an answered step. History in node_attempts is preserved."""
    node = challenge.node(node_id)
    if node is None or node.type is NodeType.input:
        raise AttemptError("this step cannot be retried")

    progress = attempt.nodes.setdefault(node_id, NodeProgress())
    progress.status = NodeStatus.available
    progress.classification = None
    progress.solved_at = None

    if attempt.status is AttemptStatus.completed:
        attempt.status = AttemptStatus.in_progress
        attempt.completed_at = None

    attempt.current_node_id = recompute_availability(challenge, attempt.nodes)
    # The user asked to redo this step, so make it the active one even if an
    # earlier step is also open.
    if attempt.nodes[node_id].status is NodeStatus.available:
        if attempt.current_node_id and attempt.current_node_id != node_id:
            attempt.nodes[attempt.current_node_id].status = NodeStatus.available
        attempt.nodes[node_id].status = NodeStatus.active
        attempt.current_node_id = node_id

    attempt.last_activity_at = utcnow()
    await _save(attempt)
    return attempt


async def reveal_hint(
    challenge: Challenge, attempt: ChallengeAttempt, node_id: str
) -> tuple[str, int, int]:
    node = _require_answerable(challenge, attempt, node_id)
    if not node.hints:
        raise AttemptError("no hints for this step")

    progress = attempt.nodes[node_id]
    index = min(progress.hints_revealed, len(node.hints) - 1)
    progress.hints_revealed = min(progress.hints_revealed + 1, len(node.hints))
    progress.used_hint = True
    attempt.last_activity_at = utcnow()
    await _save(attempt)
    return node.hints[index], progress.hints_revealed, len(node.hints)


async def save_calculation_draft(
    attempt: ChallengeAttempt, node_id: str, calculation: str | None
) -> None:
    """Keep rough work even when the estimate has not been submitted."""
    progress = attempt.nodes.setdefault(node_id, NodeProgress())
    progress.last_calculation = calculation
    attempt.last_activity_at = utcnow()
    await _save(attempt)


async def abandon_stale_attempt(attempt: ChallengeAttempt) -> None:
    attempt.status = AttemptStatus.abandoned
    await _save(attempt)


def solved_count(challenge: Challenge, attempt: ChallengeAttempt) -> int:
    return sum(
        1
        for node in challenge.estimate_nodes
        if attempt.nodes.get(node.id, NodeProgress()).status in RESOLVED_STATUSES
    )


def elapsed_seconds(attempt: ChallengeAttempt, until: datetime | None = None) -> int:
    reference = until or attempt.completed_at or attempt.last_activity_at
    return max(0, int((reference - attempt.started_at).total_seconds()))
