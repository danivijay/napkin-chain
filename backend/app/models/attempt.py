"""User attempts: what the user DID.

Two documents, on purpose:
  * ``challenge_attempts`` - resumable state of one run through a chain.
  * ``node_attempts``      - an append-only log of every estimate submitted.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import (
    AttemptStatus,
    Classification,
    Document,
    Mode,
    NodeStatus,
    utcnow,
)


class NodeProgress(BaseModel):
    """Per-node state inside a challenge attempt."""

    model_config = ConfigDict(populate_by_name=True)

    status: NodeStatus = NodeStatus.locked
    attempts: int = 0
    used_hint: bool = Field(default=False, alias="usedHint")
    hints_revealed: int = Field(default=0, alias="hintsRevealed")
    best_ratio: float | None = Field(default=None, alias="bestRatio")
    last_ratio: float | None = Field(default=None, alias="lastRatio")
    last_estimate: float | None = Field(default=None, alias="lastEstimate")
    last_calculation: str | None = Field(default=None, alias="lastCalculation")
    classification: Classification | None = None
    time_spent_seconds: int = Field(default=0, alias="timeSpentSeconds")
    solved_at: datetime | None = Field(default=None, alias="solvedAt")


class ChallengeAttempt(Document):
    user_id: str = Field(alias="userId")
    challenge_id: str = Field(alias="challengeId")
    challenge_slug: str = Field(alias="challengeSlug")
    mode: Mode
    status: AttemptStatus = AttemptStatus.in_progress
    current_node_id: str | None = Field(default=None, alias="currentNodeId")
    nodes: dict[str, NodeProgress] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=utcnow, alias="startedAt")
    last_activity_at: datetime = Field(default_factory=utcnow, alias="lastActivityAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    time_spent_seconds: int = Field(default=0, alias="timeSpentSeconds")
    score: float | None = None
    average_ratio: float | None = Field(default=None, alias="averageRatio")


class NodeAttempt(Document):
    """One submitted estimate. Never mutated - this is the analytics substrate."""

    user_id: str = Field(alias="userId")
    challenge_id: str = Field(alias="challengeId")
    challenge_attempt_id: str = Field(alias="challengeAttemptId")
    node_id: str = Field(alias="nodeId")
    concept_id: str | None = Field(default=None, alias="conceptId")
    mode: Mode
    attempt_number: int = Field(alias="attemptNumber")
    estimate: float
    expected_value: float = Field(alias="expectedValue")
    expected_min: float | None = Field(default=None, alias="expectedMin")
    expected_max: float | None = Field(default=None, alias="expectedMax")
    ratio: float
    classification: Classification
    time_spent_seconds: int = Field(default=0, alias="timeSpentSeconds")
    used_hint: bool = Field(default=False, alias="usedHint")
    calculation: str | None = None
    created_at: datetime = Field(default_factory=utcnow, alias="createdAt")
