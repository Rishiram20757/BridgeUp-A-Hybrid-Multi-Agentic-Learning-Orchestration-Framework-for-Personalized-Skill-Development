from typing import List, Literal, Optional, Dict
from pydantic import BaseModel, Field


# --------------------------------------------
# 1. Strategy Suggestion
# --------------------------------------------

class StrategySuggestion(BaseModel):
    suggested_strategy: Literal["FAST", "BALANCED", "DEEP"]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_summary: str
    tradeoffs: List[str]


# --------------------------------------------
# 2. Roadmap Explanation
# --------------------------------------------

class RoadmapExplanation(BaseModel):
    roadmap_summary: str
    phase_explanations: List[str]
    learning_strategy_rationale: str
    expected_outcome: str


# --------------------------------------------
# 3. Monitoring Feedback
# --------------------------------------------

class MonitoringFeedback(BaseModel):
    performance_summary: str
    detected_issues: List[str]
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    recommended_adjustments: List[str]
    motivational_feedback: str


# --------------------------------------------
# 4. API Query Intent (Future Tool Calling)
# --------------------------------------------

class APIQueryIntent(BaseModel):
    intent_type: Literal[
        "FETCH_JOB_MARKET_DATA",
        "FETCH_CERTIFICATION_COURSES",
        "FETCH_SALARY_TRENDS",
        "NO_EXTERNAL_QUERY"
    ]
    required_parameters: Dict[str, str]
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    reasoning: str


class ReflectionFeedback(BaseModel):
    overall_assessment: str
    detected_patterns: List[str]
    potential_risks: List[str]
    coaching_advice: List[str]


from typing import List, Dict
from pydantic import BaseModel


class RankedResource(BaseModel):

    title: str
    explanation: str


class RankedResources(BaseModel):

    ranked_jobs: List[RankedResource]

    ranked_courses: List[RankedResource]

    ranked_projects: List[RankedResource]

    ranked_tutorials: List[RankedResource]


class LearningPhase(BaseModel):

    phase_name: str

    objective: str

    recommended_resources: List[str]


class LearningRecommendation(BaseModel):

    summary: str

    recommended_resources: Dict[str, List[str]]

    learning_phases: List[LearningPhase]

    career_outlook: str