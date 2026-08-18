"""Mastery scoring: accuracy, consistency, speed, difficulty."""

import pytest

from app.models.common import Classification, Difficulty, MasteryStatus
from app.services.mastery_service import (
    EMPTY_SNAPSHOT,
    MasteryInput,
    apply_attempt,
    classify_status,
    sample_score,
)


def attempt(**overrides) -> MasteryInput:
    defaults = dict(
        classification=Classification.excellent,
        ratio=1.0,
        passed=True,
        attempt_number=1,
        used_hint=False,
        seconds=90,
        difficulty=Difficulty.builder,
    )
    return MasteryInput(**{**defaults, **overrides})


def test_a_single_perfect_estimate_is_not_mastery():
    result = apply_attempt(EMPTY_SNAPSHOT, attempt())
    assert result.mastery <= 0.5
    assert result.status is not MasteryStatus.mastered


def test_repeated_success_builds_mastery():
    snapshot = EMPTY_SNAPSHOT
    for _ in range(6):
        snapshot = apply_attempt(snapshot, attempt())
    assert snapshot.mastery >= 0.85
    assert snapshot.status is MasteryStatus.mastered


def test_a_bad_estimate_pulls_mastery_down():
    strong = EMPTY_SNAPSHOT
    for _ in range(5):
        strong = apply_attempt(strong, attempt())
    after = apply_attempt(strong, attempt(classification=Classification.needs_review, ratio=20, passed=False))
    assert after.mastery < strong.mastery


def test_hints_and_retries_are_worth_less():
    assert sample_score(attempt(used_hint=True)) < sample_score(attempt())
    assert sample_score(attempt(attempt_number=3)) < sample_score(attempt(attempt_number=1))


def test_harder_challenges_are_worth_more():
    assert sample_score(attempt(difficulty=Difficulty.interview)) > sample_score(
        attempt(difficulty=Difficulty.foundation)
    )


def test_slow_answers_score_slightly_lower_than_fast_ones():
    assert sample_score(attempt(seconds=300)) < sample_score(attempt(seconds=30))


def test_running_statistics_track_the_attempt_history():
    snapshot = apply_attempt(EMPTY_SNAPSHOT, attempt(ratio=1.0, seconds=60))
    snapshot = apply_attempt(snapshot, attempt(ratio=3.0, seconds=120, classification=Classification.good))
    assert snapshot.attempts == 2
    assert snapshot.solved == 2
    assert snapshot.average_ratio == pytest.approx(2.0)
    assert snapshot.best_ratio == pytest.approx(1.0)
    assert snapshot.average_seconds == pytest.approx(90.0)


def test_failed_attempts_count_as_practice_but_not_as_solved():
    snapshot = apply_attempt(EMPTY_SNAPSHOT, attempt(passed=False, classification=Classification.needs_review, ratio=15))
    assert snapshot.attempts == 1
    assert snapshot.solved == 0


def test_status_thresholds():
    assert classify_status(0.0, 0) is MasteryStatus.untouched
    assert classify_status(0.2, 1) is MasteryStatus.learning
    assert classify_status(0.5, 3) is MasteryStatus.developing
    assert classify_status(0.75, 3) is MasteryStatus.strong
    assert classify_status(0.9, 2) is MasteryStatus.strong  # not enough evidence yet
    assert classify_status(0.9, 5) is MasteryStatus.mastered
