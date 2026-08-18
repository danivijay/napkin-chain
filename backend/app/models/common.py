"""Shared building blocks for persisted documents.

Every document carries an explicit ``schemaVersion`` so the shape can evolve
without guessing at what an old document meant.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any

from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _to_str_id(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    return value


DocumentId = Annotated[str, BeforeValidator(_to_str_id)]


def utcnow() -> datetime:
    return datetime.now(UTC)


class Document(BaseModel):
    """Base for documents read out of MongoDB."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: DocumentId = Field(alias="_id")
    schema_version: int = Field(default=1, alias="schemaVersion")


class Difficulty(StrEnum):
    foundation = "foundation"
    builder = "builder"
    system = "system"
    interview = "interview"


class Mode(StrEnum):
    learn = "learn"
    practice = "practice"
    interview = "interview"


class NodeType(StrEnum):
    input = "input"
    estimate = "estimate"


class NodeStatus(StrEnum):
    locked = "locked"
    available = "available"
    active = "active"
    solved = "solved"
    weak = "weak"
    mastered = "mastered"


class AttemptStatus(StrEnum):
    in_progress = "in_progress"
    completed = "completed"
    abandoned = "abandoned"


class Classification(StrEnum):
    """Ratio-based buckets. Napkin math is about order of magnitude."""

    excellent = "excellent"
    very_good = "very_good"
    good = "good"
    developing = "developing"
    needs_review = "needs_review"


class ConceptArea(StrEnum):
    traffic = "traffic"
    storage = "storage"
    bandwidth = "bandwidth"
    capacity = "capacity"
    assumptions = "assumptions"


class MasteryStatus(StrEnum):
    untouched = "untouched"
    learning = "learning"
    developing = "developing"
    strong = "strong"
    mastered = "mastered"
