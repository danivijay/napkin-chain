"""Concept definitions: small, standalone estimation skills.

A concept is deliberately learnable in 1-3 minutes, so a user can leave a
challenge mid-step, learn the thing they lack, and come straight back.
"""

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import ConceptArea, Document


class ConceptExample(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    given: str
    working: list[str] = Field(default_factory=list)
    result: str


class ConceptDrill(BaseModel):
    """The 'Try it' step at the end of a concept."""

    model_config = ConfigDict(populate_by_name=True)

    prompt: str
    given: str
    unit: str = ""
    expected_min: float = Field(alias="expectedMin")
    expected_max: float = Field(alias="expectedMax")
    explanation: list[str] = Field(default_factory=list)


class Concept(Document):
    concept_id: str = Field(alias="conceptId")
    title: str
    area: ConceptArea
    order: int = 0
    one_liner: str = Field(alias="oneLiner")
    read_minutes: int = Field(default=2, alias="readMinutes")
    explanation: list[str] = Field(default_factory=list)
    shortcut: str | None = None
    shortcut_note: str | None = Field(default=None, alias="shortcutNote")
    examples: list[ConceptExample] = Field(default_factory=list)
    pitfalls: list[str] = Field(default_factory=list)
    drill: ConceptDrill | None = None
    related_concept_ids: list[str] = Field(default_factory=list, alias="relatedConceptIds")
    related_challenge_slugs: list[str] = Field(
        default_factory=list, alias="relatedChallengeSlugs"
    )
