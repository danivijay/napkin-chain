"""The evaluation engine: ratio, classification, node status."""

import pytest

from app.models.challenge import ChallengeNode, Thresholds
from app.models.common import Classification, NodeStatus, NodeType
from app.services.evaluation_service import (
    chain_score,
    compute_ratio,
    evaluate_estimate,
    node_status_for,
)

RANGE_NODE = ChallengeNode(
    id="avg_qps",
    type=NodeType.estimate,
    label="Average QPS",
    unit="QPS",
    expectedMin=8_000,
    expectedMax=15_000,
)

POINT_NODE = ChallengeNode(
    id="peak_qps",
    type=NodeType.estimate,
    label="Peak QPS",
    unit="QPS",
    expectedValue=30_000,
)


def test_target_of_a_range_is_the_geometric_midpoint():
    # An arithmetic mean would sit too near the top of an order-of-magnitude range.
    assert RANGE_NODE.target == pytest.approx((8_000 * 15_000) ** 0.5)


@pytest.mark.parametrize("estimate", [8_000, 10_000, 15_000])
def test_anything_inside_the_range_scores_a_ratio_of_one(estimate):
    ratio, direction, within = compute_ratio(RANGE_NODE, estimate)
    assert (ratio, direction, within) == (1.0, "within", True)


def test_ratio_is_measured_from_the_nearest_bound():
    assert compute_ratio(RANGE_NODE, 30_000)[0] == pytest.approx(2.0)  # 2x above max
    assert compute_ratio(RANGE_NODE, 4_000)[0] == pytest.approx(2.0)  # 2x below min


def test_direction_is_reported_separately_from_magnitude():
    assert compute_ratio(RANGE_NODE, 30_000)[1] == "over"
    assert compute_ratio(RANGE_NODE, 4_000)[1] == "under"


def test_point_estimates_are_symmetric():
    assert compute_ratio(POINT_NODE, 60_000)[0] == pytest.approx(2.0)
    assert compute_ratio(POINT_NODE, 15_000)[0] == pytest.approx(2.0)


def test_non_positive_estimates_are_rejected():
    with pytest.raises(ValueError):
        compute_ratio(POINT_NODE, 0)


@pytest.mark.parametrize(
    ("estimate", "expected"),
    [
        (30_000, Classification.excellent),      # 1.0x - inside the range
        (20_000, Classification.excellent),      # 1.5x
        (55_000, Classification.very_good),      # 1.83x
        (100_000, Classification.good),          # 3.3x
        (250_000, Classification.developing),    # 8.3x
        (1_000_000, Classification.needs_review),  # 33x
    ],
)
def test_classification_buckets(estimate, expected):
    assert evaluate_estimate(POINT_NODE, estimate, Thresholds()).classification is expected


def test_thresholds_are_configurable_per_challenge():
    strict = Thresholds(excellent=1.05, veryGood=1.1, good=1.2, developing=1.4)
    # 50K against a 30K target is 1.67x: comfortable by default, a miss under
    # tighter thresholds.
    assert (
        evaluate_estimate(POINT_NODE, 50_000, Thresholds()).classification
        is Classification.very_good
    )
    assert (
        evaluate_estimate(POINT_NODE, 50_000, strict).classification
        is Classification.needs_review
    )


def test_good_still_counts_as_passing_but_developing_does_not():
    assert evaluate_estimate(POINT_NODE, 100_000, Thresholds()).passed is True
    assert evaluate_estimate(POINT_NODE, 250_000, Thresholds()).passed is False


def test_mastery_of_a_node_requires_first_try_no_hint_excellent():
    excellent = evaluate_estimate(POINT_NODE, 30_000, Thresholds())
    assert node_status_for(excellent, attempt_number=1, used_hint=False) is NodeStatus.mastered
    assert node_status_for(excellent, attempt_number=2, used_hint=False) is NodeStatus.solved
    assert node_status_for(excellent, attempt_number=1, used_hint=True) is NodeStatus.solved

    weak = evaluate_estimate(POINT_NODE, 900_000, Thresholds())
    assert node_status_for(weak, attempt_number=1, used_hint=False) is NodeStatus.weak


def test_chain_score_averages_quality_not_correctness():
    perfect = evaluate_estimate(POINT_NODE, 30_000, Thresholds())
    poor = evaluate_estimate(POINT_NODE, 1_000_000, Thresholds())
    assert chain_score([perfect, perfect]) == 1.0
    assert 0.5 < chain_score([perfect, poor]) < 0.6
    assert chain_score([]) == 0.0
