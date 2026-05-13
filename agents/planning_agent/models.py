"""
In-memory data models used by the BridgeUp Planning Agent.

These models define how the Planning Agent represents:
- Dataset entities (D1–D4)
- Internal reasoning structures

No planning logic is implemented here.
"""

from dataclasses import dataclass
from typing import List, Optional

from enum import Enum
class MasteryLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class PlanStrategy(Enum):
    FAST = "fast"
    BALANCED = "balanced"
    DEEP = "deep"

# =========================
# Dataset-Aligned Models
# =========================

@dataclass(frozen=True)
class LearningResource:
    resource_id: str
    title: str
    provider: str
    domain: str
    skill_tags: List[str]
    difficulty: str
    duration_hours: float
    cost_type: str
    url: str


@dataclass(frozen=True)
class Skill:
    skill_id: str
    skill_name: str
    domain: str
    parent_skill: Optional[str]
    level: int
    description: str


@dataclass(frozen=True)
class JobSkillRequirement:
    job_role_id: str
    job_role_name: str
    required_skills: List[str]
    skill_weightage: List[float]
    domain: str


@dataclass(frozen=True)
class SkillPrerequisite:
    skill_id: str
    prerequisite_skill_id: str
    dependency_type: str  # "hard" | "soft"


# =========================
# Agent Internal Models
# =========================

@dataclass
class SkillNode:
    skill_id: str
    skill_name: str
    domain: str

    weight: float

    hard_prerequisites: List[str]
    soft_prerequisites: List[str]

    is_known: bool = False


@dataclass
class ResourceAssignment:
    resource_id: str
    skill_id: str
    duration_hours: float


@dataclass
class RoadmapStep:
    order: int
    skill_id: str
    skill_name: str
    mastery_level: MasteryLevel
    resources: List[ResourceAssignment]
    total_hours: float


@dataclass
class LearningRoadmap:
    target_job_role: str
    weekly_time_hours: float
    steps: List[RoadmapStep]
#############################################

from dataclasses import dataclass
from typing import List


@dataclass
class WeeklyPlan:
    week_number: int
    skill_id: str
    allocated_hours: float
    resources: List[str]

###############

from dataclasses import dataclass
from typing import List

@dataclass
class ExplainabilityNote:
    skill_id: str
    reasons: List[str]

#######

