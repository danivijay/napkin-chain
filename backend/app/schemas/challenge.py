"""View models for challenges and the chain workspace.

The rule enforced here: a node's expected value, explanation and unrevealed
hints never leave the server until the user has actually submitted an
estimate for that node.
"""

from datetime import datetime

from app.models.challenge import Challenge, ChallengeNode, Given
from app.models.common import Difficulty, Mode, NodeStatus, NodeType
from app.schemas.common import CamelModel

_RESOLVED = {NodeStatus.solved, NodeStatus.weak, NodeStatus.mastered}


class GivenOut(CamelModel):
    label: str
    value: str


class ChainNodeOut(CamelModel):
    """One node as drawn on the napkin."""

    id: str
    label: str
    unit: str = ""
    type: NodeType
    depends_on: list[str] = []
    concept_id: str | None = None
    status: NodeStatus
    display_value: str | None = None
    attempts: int = 0
    classification: str | None = None


class ChallengeSummary(CamelModel):
    id: str
    slug: str
    title: str
    subtitle: str = ""
    description: str
    difficulty: Difficulty
    estimated_minutes: int
    modes: list[Mode]
    node_count: int
    chain_labels: list[str]
    concept_ids: list[str]
    # Overlay from the user's most recent attempt, when there is one.
    attempt_status: str | None = None
    attempt_mode: Mode | None = None
    solved_count: int = 0
    last_activity_at: datetime | None = None


class ChallengeDetail(ChallengeSummary):
    scenario_description: str
    scenario_givens: list[GivenOut] = []
    chain: list[ChainNodeOut]
    concepts: list["ConceptSummary"] = []
    suggested_seconds_per_node: int = 90


class ConceptSummary(CamelModel):
    concept_id: str
    title: str
    area: str
    one_liner: str
    read_minutes: int = 2
    order: int = 0
    mastery: float = 0.0
    status: str = "untouched"
    attempts: int = 0
    learned: bool = False
    last_practiced_at: datetime | None = None


class NodeQuestion(CamelModel):
    """Everything the user is allowed to see while answering a node."""

    id: str
    label: str
    unit: str = ""
    type: NodeType
    status: NodeStatus
    prompt: str | None = None
    givens: list[GivenOut] = []
    depends_on: list[str] = []
    concept_id: str | None = None
    concept_title: str | None = None
    attempts: int = 0
    hints_revealed: int = 0
    hints_available: int = 0
    hints: list[str] = []
    last_estimate: float | None = None
    last_calculation: str | None = None
    step_number: int = 1
    total_steps: int = 1


def given_out(given: Given) -> GivenOut:
    return GivenOut(label=given.label, value=given.value)


def concept_title_lookup(concepts: dict[str, str], node: ChallengeNode) -> str | None:
    return concepts.get(node.concept_id or "")


def chain_labels(challenge: Challenge) -> list[str]:
    return [n.label for n in challenge.nodes]


ChallengeDetail.model_rebuild()
