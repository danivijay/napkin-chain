"""Deterministic recommendations.

Deliberately a set of readable rules, kept behind one function so it can be
replaced by something adaptive without touching the API layer.
"""

from datetime import UTC, datetime, timedelta

from app.models.attempt import ChallengeAttempt
from app.models.challenge import Challenge
from app.models.common import AttemptStatus, ConceptArea, Difficulty, MasteryStatus
from app.models.concept import Concept
from app.models.progress import ConceptProgress

#: Traffic first: nothing else in a capacity estimate can be derived without it.
_TEACHING_ORDER = [
    ConceptArea.traffic,
    ConceptArea.storage,
    ConceptArea.bandwidth,
    ConceptArea.capacity,
    ConceptArea.assumptions,
]

WEAK_MASTERY = 0.5
REVIEW_AFTER_DAYS = 10

_NEXT_LEVEL: dict[Difficulty, Difficulty] = {
    Difficulty.foundation: Difficulty.builder,
    Difficulty.builder: Difficulty.system,
    Difficulty.system: Difficulty.interview,
}


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def build_recommendations(
    concepts: list[Concept],
    progress: dict[str, ConceptProgress],
    challenges: list[Challenge],
    attempts: list[ChallengeAttempt],
    limit: int = 4,
) -> list[dict]:
    concept_by_id = {c.concept_id: c for c in concepts}
    recommendations: list[dict] = []
    now = datetime.now(UTC)

    # 1. Concepts the user is actively getting wrong.
    struggling = sorted(
        (
            p
            for p in progress.values()
            if p.attempts >= 2 and p.mastery < WEAK_MASTERY and p.concept_id in concept_by_id
        ),
        key=lambda p: p.mastery,
    )
    for item in struggling[:2]:
        concept = concept_by_id[item.concept_id]
        learned = item.learned
        recommendations.append(
            {
                "kind": "learn_concept" if not learned else "practice_concept",
                "title": concept.title,
                "reason": (
                    f"You've been about {item.average_ratio:.1f}x off here."
                    if item.average_ratio
                    else "This one has been shaky."
                ),
                "action_label": "Learn" if not learned else "Practice",
                "concept_id": concept.concept_id,
                "priority": 100 - int(item.mastery * 100),
            }
        )

    # 2. Concepts never touched, offered in teaching order rather than in the
    #    library's alphabetical grouping.
    untouched = sorted(
        (c for c in concepts if c.concept_id not in progress),
        key=lambda c: (_TEACHING_ORDER.index(c.area), c.order),
    )
    if untouched and len(recommendations) < limit:
        concept = untouched[0]
        recommendations.append(
            {
                "kind": "learn_concept",
                "title": concept.title,
                "reason": "You haven't covered this yet.",
                "action_label": "Learn",
                "concept_id": concept.concept_id,
                "priority": 40,
            }
        )

    # 3. Strong concepts going stale.
    stale = [
        p
        for p in progress.values()
        if p.status in {MasteryStatus.strong, MasteryStatus.mastered}
        and (last := _aware(p.last_practiced_at))
        and (now - last) > timedelta(days=REVIEW_AFTER_DAYS)
        and p.concept_id in concept_by_id
    ]
    for item in stale[:1]:
        concept = concept_by_id[item.concept_id]
        recommendations.append(
            {
                "kind": "review_concept",
                "title": concept.title,
                "reason": "Solid before, but not practiced recently.",
                "action_label": "Review",
                "concept_id": concept.concept_id,
                "priority": 30,
            }
        )

    # 4. Level up, or start somewhere sensible.
    completed = [a for a in attempts if a.status is AttemptStatus.completed]
    completed_slugs = {a.challenge_slug for a in completed}
    attempted_slugs = {a.challenge_slug for a in attempts}

    levels_done: dict[Difficulty, int] = {}
    challenge_by_slug = {c.slug: c for c in challenges}
    for attempt in completed:
        challenge = challenge_by_slug.get(attempt.challenge_slug)
        if challenge:
            levels_done[challenge.difficulty] = levels_done.get(challenge.difficulty, 0) + 1

    target_level = Difficulty.foundation
    for level, next_level in _NEXT_LEVEL.items():
        if levels_done.get(level, 0) >= 2:
            target_level = next_level

    candidates = [
        c
        for c in challenges
        if c.slug not in attempted_slugs and c.difficulty == target_level
    ] or [c for c in challenges if c.slug not in completed_slugs]

    if candidates:
        challenge = candidates[0]
        stepped_up = challenge.difficulty != Difficulty.foundation and levels_done
        recommendations.append(
            {
                "kind": "level_up" if stepped_up else "new_challenge",
                "title": challenge.title,
                "reason": (
                    f"You're ready for a {challenge.difficulty.value} chain."
                    if stepped_up
                    else f"{challenge.difficulty.value.title()} · ~{challenge.estimated_minutes} min"
                ),
                "action_label": "Start",
                "challenge_slug": challenge.slug,
                "priority": 20,
            }
        )

    recommendations.sort(key=lambda r: -r["priority"])
    return recommendations[:limit]


def weak_concepts_for_attempt(
    challenge: Challenge, attempt: ChallengeAttempt
) -> list[str]:
    from app.models.common import NodeStatus

    weak: list[str] = []
    for node in challenge.estimate_nodes:
        progress = attempt.nodes.get(node.id)
        if progress and progress.status is NodeStatus.weak and node.concept_id:
            if node.concept_id not in weak:
                weak.append(node.concept_id)
    return weak
