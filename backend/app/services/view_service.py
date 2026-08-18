"""Domain objects -> API view models.

Also the single place that decides what a user is allowed to see: expected
values, explanations and unrevealed hints stay server-side until the node has
actually been attempted.
"""

from app.models.attempt import ChallengeAttempt, NodeProgress
from app.models.challenge import Challenge, ChallengeNode
from app.models.common import NodeStatus, NodeType
from app.models.concept import Concept
from app.models.progress import ConceptProgress
from app.schemas.attempt import (
    AttemptStateOut,
    ChallengeResultOut,
    FeedbackOut,
    NodeResultOut,
)
from app.schemas.challenge import (
    ChainNodeOut,
    ChallengeDetail,
    ChallengeSummary,
    ConceptSummary,
    GivenOut,
    NodeQuestion,
)
from app.schemas.concept import (
    ConceptDetail,
    ConceptDrillOut,
    ConceptExampleOut,
    RelatedChallengeOut,
)
from app.services import attempt_service
from app.services.attempt_service import RESOLVED_STATUSES, display_value
from app.services.evaluation_service import Evaluation


def chain_node_out(
    challenge: Challenge, node: ChallengeNode, progress: NodeProgress
) -> ChainNodeOut:
    return ChainNodeOut(
        id=node.id,
        label=node.label,
        unit=node.unit,
        type=node.type,
        depends_on=node.depends_on,
        concept_id=node.concept_id,
        status=progress.status,
        display_value=display_value(challenge, node, progress),
        attempts=progress.attempts,
        classification=progress.classification.value if progress.classification else None,
    )


def chain_out(challenge: Challenge, attempt: ChallengeAttempt | None) -> list[ChainNodeOut]:
    nodes = attempt.nodes if attempt else attempt_service.initial_nodes(challenge)
    return [
        chain_node_out(challenge, node, nodes.get(node.id, NodeProgress()))
        for node in challenge.nodes
    ]


def question_out(
    challenge: Challenge,
    node: ChallengeNode,
    progress: NodeProgress,
    concept_titles: dict[str, str],
) -> NodeQuestion:
    estimate_nodes = challenge.estimate_nodes
    step_number = next(
        (i + 1 for i, n in enumerate(estimate_nodes) if n.id == node.id), 1
    )
    return NodeQuestion(
        id=node.id,
        label=node.label,
        unit=node.unit,
        type=node.type,
        status=progress.status,
        prompt=node.prompt,
        givens=[GivenOut(label=g.label, value=g.value) for g in node.givens],
        depends_on=node.depends_on,
        concept_id=node.concept_id,
        concept_title=concept_titles.get(node.concept_id or ""),
        attempts=progress.attempts,
        hints_revealed=progress.hints_revealed,
        hints_available=len(node.hints),
        hints=node.hints[: progress.hints_revealed],
        last_estimate=progress.last_estimate,
        last_calculation=progress.last_calculation,
        step_number=step_number,
        total_steps=len(estimate_nodes),
    )


def attempt_state_out(
    challenge: Challenge,
    attempt: ChallengeAttempt,
    concept_titles: dict[str, str],
) -> AttemptStateOut:
    question = None
    if attempt.current_node_id:
        node = challenge.node(attempt.current_node_id)
        if node:
            question = question_out(
                challenge,
                node,
                attempt.nodes.get(node.id, NodeProgress()),
                concept_titles,
            )

    return AttemptStateOut(
        attempt_id=attempt.id,
        challenge_slug=challenge.slug,
        challenge_title=challenge.title,
        mode=attempt.mode,
        status=attempt.status,
        chain=chain_out(challenge, attempt),
        current_node_id=attempt.current_node_id,
        question=question,
        solved_count=attempt_service.solved_count(challenge, attempt),
        total_steps=len(challenge.estimate_nodes),
        started_at=attempt.started_at,
        last_activity_at=attempt.last_activity_at,
        time_spent_seconds=attempt.time_spent_seconds,
        suggested_seconds_per_node=challenge.suggested_seconds_per_node,
        score=attempt.score,
        average_ratio=attempt.average_ratio,
    )


def feedback_out(
    node: ChallengeNode,
    evaluation: Evaluation,
    node_status: NodeStatus,
    concept_titles: dict[str, str],
) -> FeedbackOut:
    return FeedbackOut(
        headline=evaluation.headline,
        classification=evaluation.classification,
        passed=evaluation.passed,
        ratio=evaluation.ratio,
        direction=evaluation.direction,
        within_range=evaluation.within_range,
        your_estimate=evaluation.estimate,
        expected_value=round(evaluation.target, 4),
        expected_min=evaluation.expected_min,
        expected_max=evaluation.expected_max,
        unit=node.unit,
        explanation_steps=node.explanation.steps,
        shortcut=node.explanation.shortcut,
        note=node.explanation.note,
        concept_id=node.concept_id,
        concept_title=concept_titles.get(node.concept_id or ""),
        node_status=node_status,
    )


def challenge_summary(
    challenge: Challenge, attempt: ChallengeAttempt | None = None
) -> ChallengeSummary:
    return ChallengeSummary(
        id=challenge.id,
        slug=challenge.slug,
        title=challenge.title,
        subtitle=challenge.subtitle,
        description=challenge.description,
        difficulty=challenge.difficulty,
        estimated_minutes=challenge.estimated_minutes,
        modes=challenge.modes,
        node_count=len(challenge.estimate_nodes),
        chain_labels=[n.label for n in challenge.nodes],
        concept_ids=challenge.concept_ids,
        attempt_status=attempt.status.value if attempt else None,
        attempt_mode=attempt.mode if attempt else None,
        solved_count=attempt_service.solved_count(challenge, attempt) if attempt else 0,
        last_activity_at=attempt.last_activity_at if attempt else None,
    )


def challenge_detail(
    challenge: Challenge,
    attempt: ChallengeAttempt | None,
    concepts: list[Concept],
    progress: dict[str, ConceptProgress],
) -> ChallengeDetail:
    summary = challenge_summary(challenge, attempt)
    return ChallengeDetail(
        **summary.model_dump(),
        scenario_description=challenge.scenario.description,
        scenario_givens=[
            GivenOut(label=g.label, value=g.value) for g in challenge.scenario.givens
        ],
        chain=chain_out(challenge, attempt),
        concepts=[concept_summary(c, progress.get(c.concept_id)) for c in concepts],
        suggested_seconds_per_node=challenge.suggested_seconds_per_node,
    )


def concept_summary(
    concept: Concept, progress: ConceptProgress | None = None
) -> ConceptSummary:
    return ConceptSummary(
        concept_id=concept.concept_id,
        title=concept.title,
        area=concept.area.value,
        one_liner=concept.one_liner,
        read_minutes=concept.read_minutes,
        order=concept.order,
        mastery=progress.mastery if progress else 0.0,
        status=progress.status.value if progress else "untouched",
        attempts=progress.attempts if progress else 0,
        learned=progress.learned if progress else False,
        last_practiced_at=progress.last_practiced_at if progress else None,
    )


def concept_detail(
    concept: Concept,
    progress: ConceptProgress | None,
    related_concepts: list[Concept],
    related_challenges: list[Challenge],
    progress_map: dict[str, ConceptProgress],
) -> ConceptDetail:
    summary = concept_summary(concept, progress)
    return ConceptDetail(
        **summary.model_dump(),
        explanation=concept.explanation,
        shortcut=concept.shortcut,
        shortcut_note=concept.shortcut_note,
        examples=[
            ConceptExampleOut(given=e.given, working=e.working, result=e.result)
            for e in concept.examples
        ],
        pitfalls=concept.pitfalls,
        drill=(
            ConceptDrillOut(
                prompt=concept.drill.prompt,
                given=concept.drill.given,
                unit=concept.drill.unit,
            )
            if concept.drill
            else None
        ),
        related_concepts=[
            concept_summary(c, progress_map.get(c.concept_id)) for c in related_concepts
        ],
        related_challenges=[
            RelatedChallengeOut(
                slug=c.slug,
                title=c.title,
                difficulty=c.difficulty.value,
                estimated_minutes=c.estimated_minutes,
            )
            for c in related_challenges
        ],
    )


def challenge_result(challenge: Challenge, attempt: ChallengeAttempt) -> ChallengeResultOut:
    nodes: list[NodeResultOut] = []
    mastered = weak = 0
    for node in challenge.nodes:
        if node.type is NodeType.input:
            continue
        progress = attempt.nodes.get(node.id, NodeProgress())
        if progress.status is NodeStatus.mastered:
            mastered += 1
        if progress.status is NodeStatus.weak:
            weak += 1
        revealed = progress.status in RESOLVED_STATUSES
        nodes.append(
            NodeResultOut(
                node_id=node.id,
                label=node.label,
                unit=node.unit,
                status=progress.status,
                attempts=progress.attempts,
                your_estimate=progress.last_estimate,
                expected_value=round(node.target, 4) if revealed else None,
                ratio=progress.last_ratio,
                classification=progress.classification,
                concept_id=node.concept_id,
                time_spent_seconds=progress.time_spent_seconds,
            )
        )

    total = attempt_service.elapsed_seconds(attempt)
    solved = attempt_service.solved_count(challenge, attempt)
    from app.services.recommendation_service import weak_concepts_for_attempt

    return ChallengeResultOut(
        attempt_id=attempt.id,
        challenge_slug=challenge.slug,
        challenge_title=challenge.title,
        mode=attempt.mode,
        status=attempt.status,
        score=attempt.score,
        average_ratio=attempt.average_ratio,
        total_seconds=total,
        seconds_per_step=round(total / solved, 1) if solved else None,
        solved_count=solved,
        total_steps=len(challenge.estimate_nodes),
        mastered_count=mastered,
        weak_count=weak,
        nodes=nodes,
        weak_concept_ids=weak_concepts_for_attempt(challenge, attempt),
    )
