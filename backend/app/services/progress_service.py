"""Concept mastery and the aggregate 'system design intuition' view."""

from datetime import UTC, datetime, timedelta

from bson import ObjectId

from app.db.mongodb import Collections, collection
from app.models.attempt import ChallengeAttempt
from app.models.common import (
    AttemptStatus,
    ConceptArea,
    Difficulty,
    MasteryStatus,
    utcnow,
)
from app.models.concept import Concept
from app.models.progress import ConceptProgress
from app.services.mastery_service import (
    EMPTY_SNAPSHOT,
    MasteryInput,
    MasterySnapshot,
    apply_attempt,
    classify_status,
)

AREA_TITLES: dict[ConceptArea, str] = {
    ConceptArea.traffic: "Traffic",
    ConceptArea.storage: "Storage",
    ConceptArea.bandwidth: "Bandwidth",
    ConceptArea.capacity: "Capacity",
    ConceptArea.assumptions: "Assumptions",
}


def _snapshot(progress: ConceptProgress | None) -> MasterySnapshot:
    if progress is None:
        return EMPTY_SNAPSHOT
    return MasterySnapshot(
        mastery=progress.mastery,
        attempts=progress.attempts,
        solved=progress.solved,
        average_ratio=progress.average_ratio,
        best_ratio=progress.best_ratio,
        average_seconds=progress.average_seconds,
        status=progress.status,
    )


async def get_concept_progress(user_id: str, concept_id: str) -> ConceptProgress | None:
    doc = await collection(Collections.concept_progress).find_one(
        {"userId": user_id, "conceptId": concept_id}
    )
    return ConceptProgress.model_validate(doc) if doc else None


async def get_progress_map(user_id: str) -> dict[str, ConceptProgress]:
    docs = await (
        collection(Collections.concept_progress)
        .find({"userId": user_id})
        .to_list(length=500)
    )
    progress = [ConceptProgress.model_validate(d) for d in docs]
    return {p.concept_id: p for p in progress}


async def record_estimate(
    user_id: str,
    concept_id: str,
    *,
    classification,
    ratio: float,
    passed: bool,
    attempt_number: int,
    used_hint: bool,
    seconds: int,
    difficulty: Difficulty,
) -> ConceptProgress:
    """Fold one estimate into what we believe the user knows."""
    current = await get_concept_progress(user_id, concept_id)
    updated = apply_attempt(
        _snapshot(current),
        MasteryInput(
            classification=classification,
            ratio=ratio,
            passed=passed,
            attempt_number=attempt_number,
            used_hint=used_hint,
            seconds=seconds,
            difficulty=difficulty,
        ),
    )
    now = utcnow()
    doc = await collection(Collections.concept_progress).find_one_and_update(
        {"userId": user_id, "conceptId": concept_id},
        {
            "$set": {
                "mastery": updated.mastery,
                "attempts": updated.attempts,
                "solved": updated.solved,
                "averageRatio": updated.average_ratio,
                "bestRatio": updated.best_ratio,
                "averageSeconds": updated.average_seconds,
                "status": updated.status.value,
                "lastPracticedAt": now,
                "updatedAt": now,
            },
            "$setOnInsert": {"schemaVersion": 1, "learned": False},
        },
        upsert=True,
        return_document=True,
    )
    return ConceptProgress.model_validate(doc)


async def mark_learned(user_id: str, concept_id: str) -> ConceptProgress:
    """Reading a concept is not mastery, but it is a floor under it."""
    now = utcnow()
    existing = await get_concept_progress(user_id, concept_id)
    mastery = max(existing.mastery if existing else 0.0, 0.15)
    attempts = existing.attempts if existing else 0
    doc = await collection(Collections.concept_progress).find_one_and_update(
        {"userId": user_id, "conceptId": concept_id},
        {
            "$set": {
                "learned": True,
                "mastery": mastery,
                "status": classify_status(mastery, max(attempts, 1)).value,
                "updatedAt": now,
            },
            "$setOnInsert": {
                "schemaVersion": 1,
                "attempts": 0,
                "solved": 0,
                "lastPracticedAt": None,
            },
        },
        upsert=True,
        return_document=True,
    )
    return ConceptProgress.model_validate(doc)


def area_strengths(
    concepts: list[Concept], progress: dict[str, ConceptProgress]
) -> list[dict]:
    by_area: dict[ConceptArea, list[Concept]] = {}
    for concept in concepts:
        by_area.setdefault(concept.area, []).append(concept)

    rows = []
    for area, items in by_area.items():
        scores = [progress[c.concept_id].mastery for c in items if c.concept_id in progress]
        practiced = len(scores)
        strength = round(sum(scores) / len(items), 3) if items else 0.0
        rows.append(
            {
                "area": area.value,
                "title": AREA_TITLES[area],
                "strength": strength,
                "concept_count": len(items),
                "practiced_count": practiced,
            }
        )
    order = list(ConceptArea)
    rows.sort(key=lambda r: order.index(ConceptArea(r["area"])))
    return rows


async def _estimate_stats(user_id: str) -> dict:
    cursor = (
        collection(Collections.node_attempts)
        .find({"userId": user_id}, {"ratio": 1, "timeSpentSeconds": 1, "createdAt": 1})
        .sort("createdAt", -1)
    )
    rows = await cursor.to_list(length=2000)
    if not rows:
        return {
            "total": 0,
            "average_ratio": None,
            "seconds_per_step": None,
            "weekly": 0,
            "weekly_improvement": None,
            "days": set(),
        }

    ratios = [r["ratio"] for r in rows if r.get("ratio") is not None]
    seconds = [r.get("timeSpentSeconds") or 0 for r in rows]
    now = datetime.now(UTC)
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    def _at(row) -> datetime:
        value = row["createdAt"]
        return value if value.tzinfo else value.replace(tzinfo=UTC)

    this_week = [r for r in rows if _at(r) >= week_ago]
    last_week = [r for r in rows if two_weeks_ago <= _at(r) < week_ago]

    improvement = None
    if this_week and last_week:
        this_avg = sum(r["ratio"] for r in this_week) / len(this_week)
        last_avg = sum(r["ratio"] for r in last_week) / len(last_week)
        if this_avg > 0:
            improvement = round((last_avg - this_avg) / last_avg, 3)

    return {
        "total": len(rows),
        "average_ratio": round(sum(ratios) / len(ratios), 2) if ratios else None,
        "seconds_per_step": round(sum(seconds) / len(seconds), 1) if seconds else None,
        "weekly": len(this_week),
        "weekly_improvement": improvement,
        "days": {_at(r).date() for r in rows},
    }


def _streak(days: set) -> tuple[int, int]:
    if not days:
        return 0, 0
    ordered = sorted(days)
    best = current = 1
    for previous, day in zip(ordered, ordered[1:], strict=False):
        if (day - previous).days == 1:
            current += 1
        else:
            current = 1
        best = max(best, current)

    today = datetime.now(UTC).date()
    streak = 0
    cursor = today
    if ordered[-1] not in (today, today - timedelta(days=1)):
        return 0, best
    if ordered[-1] == today - timedelta(days=1):
        cursor = today - timedelta(days=1)
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak, best


async def build_overview(
    user_id: str,
    concepts: list[Concept],
    attempts: list[ChallengeAttempt],
) -> dict:
    progress = await get_progress_map(user_id)
    stats = await _estimate_stats(user_id)
    areas = area_strengths(concepts, progress)

    strong = sum(
        1
        for p in progress.values()
        if p.status in {MasteryStatus.strong, MasteryStatus.mastered}
    )
    mastered = sum(1 for p in progress.values() if p.status is MasteryStatus.mastered)
    completed = [a for a in attempts if a.status is AttemptStatus.completed]
    in_progress = [a for a in attempts if a.status is AttemptStatus.in_progress]

    intuition = (
        round(sum(p.mastery for p in progress.values()) / len(concepts), 3)
        if concepts
        else 0.0
    )
    streak, best_streak = _streak(stats["days"])

    return {
        "intuition": intuition,
        "skills_total": len(concepts),
        "skills_strong": strong,
        "skills_mastered": mastered,
        "chains_solved": len(completed),
        "chains_in_progress": len(in_progress),
        "average_ratio": stats["average_ratio"],
        "seconds_per_step": stats["seconds_per_step"],
        "total_estimates": stats["total"],
        "streak_days": streak,
        "best_streak_days": best_streak,
        "weekly_estimates": stats["weekly"],
        "weekly_improvement": stats["weekly_improvement"],
        "interview_ready": intuition >= 0.7 and len(completed) >= 3,
        "areas": areas,
    }


async def delete_user_progress(user_id: str) -> None:
    """Used by the profile screen's reset action and by tests."""
    for name in (
        Collections.concept_progress,
        Collections.challenge_attempts,
        Collections.node_attempts,
    ):
        await collection(name).delete_many({"userId": user_id})


async def user_exists(user_id: str) -> bool:
    return (
        await collection(Collections.users).count_documents(
            {"_id": ObjectId(user_id)}, limit=1
        )
        > 0
    )
