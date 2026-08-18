"""Challenge definitions: what a challenge IS.

Kept strictly separate from what a user did (attempt.py) and from what the
system believes a user knows (progress.py).
"""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.common import (
    Classification,
    Difficulty,
    Document,
    Mode,
    NodeType,
)


class Thresholds(BaseModel):
    """Ratio ceilings per classification. Configurable per challenge and per node."""

    model_config = ConfigDict(populate_by_name=True)

    excellent: float = 1.5
    very_good: float = Field(default=2.0, alias="veryGood")
    good: float = 5.0
    developing: float = 10.0
    # anything beyond `developing` is needs_review

    def classify(self, ratio: float) -> Classification:
        if ratio <= self.excellent:
            return Classification.excellent
        if ratio <= self.very_good:
            return Classification.very_good
        if ratio <= self.good:
            return Classification.good
        if ratio <= self.developing:
            return Classification.developing
        return Classification.needs_review


DEFAULT_THRESHOLDS = Thresholds()


class Given(BaseModel):
    """A fact handed to the user, either in the scenario or on a specific node."""

    model_config = ConfigDict(populate_by_name=True)

    label: str
    value: str


class Explanation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    steps: list[str] = Field(default_factory=list)
    shortcut: str | None = None
    note: str | None = None


class ChallengeNode(BaseModel):
    """One estimate in the chain."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    type: NodeType = NodeType.estimate
    label: str
    unit: str = ""
    depends_on: list[str] = Field(default_factory=list, alias="dependsOn")
    concept_id: str | None = Field(default=None, alias="conceptId")

    # `input` nodes: the value is given to the user, no estimate required.
    value: float | None = None
    display_value: str | None = Field(default=None, alias="displayValue")

    # `estimate` nodes.
    prompt: str | None = None
    givens: list[Given] = Field(default_factory=list)
    expected_value: float | None = Field(default=None, alias="expectedValue")
    expected_min: float | None = Field(default=None, alias="expectedMin")
    expected_max: float | None = Field(default=None, alias="expectedMax")
    hints: list[str] = Field(default_factory=list)
    explanation: Explanation = Field(default_factory=Explanation)
    thresholds: Thresholds | None = None

    @model_validator(mode="after")
    def _check_shape(self) -> "ChallengeNode":
        if self.type is NodeType.input:
            if self.value is None:
                raise ValueError(f"input node '{self.id}' needs a value")
            return self
        if self.expected_value is None and (
            self.expected_min is None or self.expected_max is None
        ):
            raise ValueError(
                f"estimate node '{self.id}' needs expectedValue or a min/max range"
            )
        return self

    @property
    def target(self) -> float:
        """The single number an estimate is scored against."""
        if self.expected_value is not None:
            return self.expected_value
        # Geometric midpoint: ranges here span orders of magnitude, so the
        # arithmetic mean would sit too close to the upper bound.
        assert self.expected_min is not None and self.expected_max is not None
        return (self.expected_min * self.expected_max) ** 0.5


class Scenario(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    description: str
    givens: list[Given] = Field(default_factory=list)


class Complexity(BaseModel):
    """Internal metadata driving future adaptive recommendations."""

    model_config = ConfigDict(populate_by_name=True)

    level: Difficulty
    chain_depth: int = Field(alias="chainDepth")
    dependency_count: int = Field(alias="dependencyCount")
    ambiguity: int = Field(ge=0, le=5)
    concept_count: int = Field(alias="conceptCount")
    time_pressure: int = Field(alias="timePressure", ge=0, le=5)


class Challenge(Document):
    slug: str
    title: str
    subtitle: str = ""
    description: str
    difficulty: Difficulty
    estimated_minutes: int = Field(alias="estimatedMinutes")
    modes: list[Mode] = Field(default_factory=lambda: list(Mode))
    scenario: Scenario
    nodes: list[ChallengeNode]
    complexity: Complexity
    thresholds: Thresholds = Field(default_factory=Thresholds)
    suggested_seconds_per_node: int = Field(default=90, alias="suggestedSecondsPerNode")

    def node(self, node_id: str) -> ChallengeNode | None:
        return next((n for n in self.nodes if n.id == node_id), None)

    def thresholds_for(self, node: ChallengeNode) -> Thresholds:
        return node.thresholds or self.thresholds

    @property
    def estimate_nodes(self) -> list[ChallengeNode]:
        return [n for n in self.nodes if n.type is NodeType.estimate]

    @property
    def concept_ids(self) -> list[str]:
        seen: list[str] = []
        for node in self.nodes:
            if node.concept_id and node.concept_id not in seen:
                seen.append(node.concept_id)
        return seen
