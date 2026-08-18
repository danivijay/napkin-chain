"""Deterministic mastery scoring.

Intentionally simple and pure: one function turns a prior mastery state plus a
new attempt into a new state. When this is replaced by something smarter, the
call sites do not change.
"""

from dataclasses import dataclass

from app.models.common import Classification, Difficulty, MasteryStatus

_QUALITY: dict[Classification, float] = {
    Classification.excellent: 1.0,
    Classification.very_good: 0.85,
    Classification.good: 0.6,
    Classification.developing: 0.3,
    Classification.needs_review: 0.05,
}

_DIFFICULTY_WEIGHT: dict[Difficulty, float] = {
    Difficulty.foundation: 0.85,
    Difficulty.builder: 1.0,
    Difficulty.system: 1.1,
    Difficulty.interview: 1.2,
}

_FAST_SECONDS = 60
_SLOW_SECONDS = 210

#: Mastery is capped by experience so a single lucky estimate never reads as
#: mastery. Roughly: 1 attempt -> 0.5, 4 -> 0.8, 6+ -> 1.0.
_CONFIDENCE_CAP_BASE = 0.4
_CONFIDENCE_CAP_STEP = 0.1


@dataclass(frozen=True)
class MasterySnapshot:
    mastery: float
    attempts: int
    solved: int
    average_ratio: float | None
    best_ratio: float | None
    average_seconds: float | None
    status: MasteryStatus


@dataclass(frozen=True)
class MasteryInput:
    classification: Classification
    ratio: float
    passed: bool
    attempt_number: int
    used_hint: bool
    seconds: int
    difficulty: Difficulty


def sample_score(item: MasteryInput) -> float:
    """Quality of a single attempt, 0-1, before smoothing."""
    score = _QUALITY[item.classification]

    if item.attempt_number > 1:
        # Getting there on a retry still counts, just less.
        score *= 0.75 ** min(item.attempt_number - 1, 3)
    if item.used_hint:
        score *= 0.8

    if item.seconds and item.seconds <= _FAST_SECONDS and item.passed:
        score = min(1.0, score * 1.05)
    elif item.seconds >= _SLOW_SECONDS:
        score *= 0.92

    score *= _DIFFICULTY_WEIGHT[item.difficulty]
    return max(0.0, min(1.0, score))


def _learning_rate(attempts: int) -> float:
    return max(0.2, 0.55 - 0.05 * attempts)


def _confidence_cap(attempts: int) -> float:
    return min(1.0, _CONFIDENCE_CAP_BASE + _CONFIDENCE_CAP_STEP * attempts)


def classify_status(mastery: float, attempts: int) -> MasteryStatus:
    if attempts == 0:
        return MasteryStatus.untouched
    if mastery >= 0.85 and attempts >= 4:
        return MasteryStatus.mastered
    if mastery >= 0.7:
        return MasteryStatus.strong
    if mastery >= 0.4:
        return MasteryStatus.developing
    return MasteryStatus.learning


def _rolling_mean(previous: float | None, count: int, value: float) -> float:
    if previous is None or count == 0:
        return value
    return (previous * count + value) / (count + 1)


def apply_attempt(previous: MasterySnapshot, item: MasteryInput) -> MasterySnapshot:
    sample = sample_score(item)
    alpha = _learning_rate(previous.attempts)
    blended = previous.mastery * (1 - alpha) + sample * alpha

    attempts = previous.attempts + 1
    mastery = round(min(blended, _confidence_cap(attempts)), 4)

    return MasterySnapshot(
        mastery=mastery,
        attempts=attempts,
        solved=previous.solved + (1 if item.passed else 0),
        average_ratio=round(
            _rolling_mean(previous.average_ratio, previous.attempts, item.ratio), 3
        ),
        best_ratio=(
            item.ratio
            if previous.best_ratio is None
            else round(min(previous.best_ratio, item.ratio), 3)
        ),
        average_seconds=round(
            _rolling_mean(
                previous.average_seconds, previous.attempts, float(item.seconds)
            ),
            1,
        ),
        status=classify_status(mastery, attempts),
    )


EMPTY_SNAPSHOT = MasterySnapshot(
    mastery=0.0,
    attempts=0,
    solved=0,
    average_ratio=None,
    best_ratio=None,
    average_seconds=None,
    status=MasteryStatus.untouched,
)
