from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from app.models.common import Document, utcnow


class EventName(StrEnum):
    signup = "signup"
    login = "login"
    logout = "logout"
    challenge_started = "challenge_started"
    challenge_completed = "challenge_completed"
    challenge_resumed = "challenge_resumed"
    challenge_reattempted = "challenge_reattempted"
    challenge_abandoned = "challenge_abandoned"
    node_attempted = "node_attempted"
    node_solved = "node_solved"
    node_retried = "node_retried"
    hint_used = "hint_used"
    concept_viewed = "concept_viewed"
    concept_learned = "concept_learned"
    concept_practiced = "concept_practiced"


class Event(Document):
    user_id: str | None = Field(default=None, alias="userId")
    name: EventName
    properties: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow, alias="createdAt")
