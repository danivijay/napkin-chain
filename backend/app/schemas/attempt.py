from datetime import datetime

from pydantic import Field

from app.models.common import AttemptStatus, Classification, Mode, NodeStatus
from app.schemas.challenge import ChainNodeOut, NodeQuestion
from app.schemas.common import CamelModel


class StartAttemptIn(CamelModel):
    mode: Mode = Mode.practice
    restart: bool = False


class EstimateIn(CamelModel):
    estimate: float = Field(gt=0, description="The user's approximate answer")
    calculation: str | None = Field(default=None, max_length=2000)
    time_spent_seconds: int = Field(default=0, ge=0, le=60 * 60 * 4)
    used_hint: bool = False


class FeedbackOut(CamelModel):
    headline: str
    classification: Classification
    passed: bool
    ratio: float
    direction: str
    within_range: bool
    your_estimate: float
    expected_value: float
    expected_min: float | None = None
    expected_max: float | None = None
    unit: str = ""
    explanation_steps: list[str] = []
    shortcut: str | None = None
    note: str | None = None
    concept_id: str | None = None
    concept_title: str | None = None
    node_status: NodeStatus


class AttemptStateOut(CamelModel):
    """The full workspace state: one request rebuilds the whole napkin."""

    attempt_id: str
    challenge_slug: str
    challenge_title: str
    mode: Mode
    status: AttemptStatus
    chain: list[ChainNodeOut]
    current_node_id: str | None = None
    question: NodeQuestion | None = None
    solved_count: int
    total_steps: int
    started_at: datetime
    last_activity_at: datetime
    time_spent_seconds: int = 0
    suggested_seconds_per_node: int = 90
    score: float | None = None
    average_ratio: float | None = None


class EstimateOut(CamelModel):
    feedback: FeedbackOut
    state: AttemptStateOut
    unlocked_node_ids: list[str] = []
    challenge_completed: bool = False


class HintOut(CamelModel):
    hint: str
    hints_revealed: int
    hints_available: int


class NodeResultOut(CamelModel):
    node_id: str
    label: str
    unit: str = ""
    status: NodeStatus
    attempts: int
    your_estimate: float | None = None
    expected_value: float | None = None
    ratio: float | None = None
    classification: Classification | None = None
    concept_id: str | None = None
    time_spent_seconds: int = 0


class ChallengeResultOut(CamelModel):
    attempt_id: str
    challenge_slug: str
    challenge_title: str
    mode: Mode
    status: AttemptStatus
    score: float | None = None
    average_ratio: float | None = None
    total_seconds: int = 0
    seconds_per_step: float | None = None
    solved_count: int
    total_steps: int
    mastered_count: int = 0
    weak_count: int = 0
    nodes: list[NodeResultOut] = []
    weak_concept_ids: list[str] = []
