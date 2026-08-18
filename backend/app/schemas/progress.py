from datetime import datetime

from app.models.common import Difficulty, Mode
from app.schemas.challenge import ConceptSummary
from app.schemas.common import CamelModel


class AreaStrengthOut(CamelModel):
    area: str
    title: str
    strength: float
    concept_count: int
    practiced_count: int


class ProgressOverview(CamelModel):
    intuition: float
    skills_total: int
    skills_strong: int
    skills_mastered: int
    chains_solved: int
    chains_in_progress: int
    average_ratio: float | None = None
    seconds_per_step: float | None = None
    total_estimates: int = 0
    streak_days: int = 0
    best_streak_days: int = 0
    weekly_estimates: int = 0
    weekly_improvement: float | None = None
    interview_ready: bool = False
    areas: list[AreaStrengthOut] = []


class SkillsOut(CamelModel):
    concepts: list[ConceptSummary] = []
    areas: list[AreaStrengthOut] = []


class ContinueCardOut(CamelModel):
    challenge_slug: str
    challenge_title: str
    difficulty: Difficulty
    mode: Mode
    solved_count: int
    total_steps: int
    last_activity_at: datetime


class RecommendationOut(CamelModel):
    kind: str  # "practice_concept" | "learn_concept" | "review_concept" | "new_challenge" | "level_up"
    title: str
    reason: str
    action_label: str
    concept_id: str | None = None
    challenge_slug: str | None = None
    priority: int = 0


class HomeOut(CamelModel):
    overview: ProgressOverview
    continue_card: ContinueCardOut | None = None
    recommendations: list[RecommendationOut] = []
    suggested_challenge_slug: str | None = None
