"""Ratio-based evaluation of a single estimate.

Napkin math is about order of magnitude, so an estimate is never simply right
or wrong: it is some factor away from a defensible answer. Everything in here
is pure so it can be tested without a database.
"""

from dataclasses import dataclass

from app.models.challenge import Challenge, ChallengeNode, Thresholds
from app.models.common import Classification, NodeStatus

#: Classifications at or above this quality count as solving the node.
PASSING = {Classification.excellent, Classification.very_good, Classification.good}

_QUALITY: dict[Classification, float] = {
    Classification.excellent: 1.0,
    Classification.very_good: 0.85,
    Classification.good: 0.65,
    Classification.developing: 0.35,
    Classification.needs_review: 0.1,
}

_HEADLINE: dict[Classification, str] = {
    Classification.excellent: "Excellent estimate",
    Classification.very_good: "Solid estimate",
    Classification.good: "Reasonable estimate",
    Classification.developing: "Off by a fair margin",
    Classification.needs_review: "This one is worth learning",
}


@dataclass(frozen=True)
class Evaluation:
    estimate: float
    ratio: float
    classification: Classification
    passed: bool
    target: float
    expected_min: float | None
    expected_max: float | None
    within_range: bool
    direction: str  # "over" | "under" | "within"
    headline: str

    @property
    def quality(self) -> float:
        return _QUALITY[self.classification]


def compute_ratio(node: ChallengeNode, estimate: float) -> tuple[float, str, bool]:
    """Return ``(ratio, direction, within_range)``.

    The ratio is always >= 1: it answers "how many times away was I?" rather
    than "was I high or low?", which the direction reports separately.
    """
    if estimate <= 0:
        raise ValueError("estimate must be greater than zero")

    lo, hi = node.expected_min, node.expected_max
    if lo is not None and hi is not None:
        if lo <= estimate <= hi:
            return 1.0, "within", True
        if estimate > hi:
            return estimate / hi, "over", False
        return lo / estimate, "under", False

    target = node.target
    if estimate >= target:
        return estimate / target, "over", False
    return target / estimate, "under", False


def evaluate_estimate(
    node: ChallengeNode, estimate: float, thresholds: Thresholds
) -> Evaluation:
    ratio, direction, within_range = compute_ratio(node, estimate)
    classification = thresholds.classify(ratio)
    return Evaluation(
        estimate=estimate,
        ratio=round(ratio, 3),
        classification=classification,
        passed=classification in PASSING,
        target=node.target,
        expected_min=node.expected_min,
        expected_max=node.expected_max,
        within_range=within_range,
        direction=direction,
        headline=_HEADLINE[classification],
    )


def evaluate_node(challenge: Challenge, node: ChallengeNode, estimate: float) -> Evaluation:
    return evaluate_estimate(node, estimate, challenge.thresholds_for(node))


def node_status_for(
    evaluation: Evaluation, *, attempt_number: int, used_hint: bool
) -> NodeStatus:
    """Mastery on a node is earned: first try, no hint, excellent estimate."""
    if not evaluation.passed:
        return NodeStatus.weak
    if (
        evaluation.classification is Classification.excellent
        and attempt_number == 1
        and not used_hint
    ):
        return NodeStatus.mastered
    return NodeStatus.solved


def chain_score(evaluations: list[Evaluation]) -> float:
    """Overall 'system design intuition' score for a completed chain, 0-1."""
    if not evaluations:
        return 0.0
    return round(sum(e.quality for e in evaluations) / len(evaluations), 3)
