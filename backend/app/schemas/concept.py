from app.schemas.challenge import ConceptSummary
from app.schemas.common import CamelModel


class ConceptExampleOut(CamelModel):
    given: str
    working: list[str] = []
    result: str


class ConceptDrillOut(CamelModel):
    prompt: str
    given: str
    unit: str = ""


class RelatedChallengeOut(CamelModel):
    slug: str
    title: str
    difficulty: str
    estimated_minutes: int


class ConceptDetail(ConceptSummary):
    explanation: list[str] = []
    shortcut: str | None = None
    shortcut_note: str | None = None
    examples: list[ConceptExampleOut] = []
    pitfalls: list[str] = []
    drill: ConceptDrillOut | None = None
    related_concepts: list[ConceptSummary] = []
    related_challenges: list[RelatedChallengeOut] = []


class ConceptGroupOut(CamelModel):
    area: str
    title: str
    concepts: list[ConceptSummary]


class DrillIn(CamelModel):
    estimate: float
    calculation: str | None = None
    time_spent_seconds: int = 0


class DrillOut(CamelModel):
    passed: bool
    ratio: float
    classification: str
    headline: str
    expected_min: float
    expected_max: float
    explanation: list[str] = []
    mastery: float
    status: str
