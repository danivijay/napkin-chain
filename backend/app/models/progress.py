"""Mastery: what the system believes the user KNOWS.

Derived from node attempts, never written by the client.
"""

from datetime import datetime

from pydantic import Field

from app.models.common import Document, MasteryStatus, utcnow


class ConceptProgress(Document):
    user_id: str = Field(alias="userId")
    concept_id: str = Field(alias="conceptId")
    mastery: float = Field(default=0.0, ge=0.0, le=1.0)
    attempts: int = 0
    solved: int = 0
    average_ratio: float | None = Field(default=None, alias="averageRatio")
    best_ratio: float | None = Field(default=None, alias="bestRatio")
    average_seconds: float | None = Field(default=None, alias="averageSeconds")
    status: MasteryStatus = MasteryStatus.untouched
    learned: bool = False
    last_practiced_at: datetime | None = Field(default=None, alias="lastPracticedAt")
    updated_at: datetime = Field(default_factory=utcnow, alias="updatedAt")
