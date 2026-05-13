import hashlib
import json

from .schemas import ReflectionFeedback
from .llm_client import LLMClient
from .prompt_templates import (
    STRATEGY_PROMPT,
    ROADMAP_EXPLANATION_PROMPT,
    MONITORING_PROMPT,
    API_INTENT_PROMPT,
    REFLECTION_PROMPT,
    RESOURCE_RANKING_PROMPT,
    RESOURCE_EXPLANATION_PROMPT,
    LEARNING_PLAN_PROMPT,
)

from .schemas import (
    StrategySuggestion,
    RoadmapExplanation,
    MonitoringFeedback,
    APIQueryIntent,
    RankedResources,
    LearningRecommendation,
)


class LLMReasoningEngine:

    def __init__(self):

        self.llm = LLMClient()

        # Roadmap explanation cache
        self.roadmap_cache = {}

        # General LLM cache
        self._cache = {}

    # =========================================
    # INTERNAL CACHE UTILITY
    # =========================================

    def _cached_generate(self, prompt, schema):

        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()

        if prompt_hash in self._cache:
            return self._cache[prompt_hash]

        result = self.llm.generate_structured(prompt, schema)

        self._cache[prompt_hash] = result

        return result

    # =========================================
    # RESOURCE TITLE EXTRACTOR
    # Handles objects OR dictionaries
    # =========================================

    def _extract_title(self, item):

        if isinstance(item, dict):
            return item.get("title") or item.get("name") or ""

        return getattr(item, "title", None) or getattr(item, "name", "") or ""

    # ----------------------------------------
    # Node 1
    # ----------------------------------------
    def analyze_user_goal(self, user_goal: str) -> APIQueryIntent:

        prompt = API_INTENT_PROMPT.format(
            user_goal=user_goal
        )

        return self._cached_generate(
            prompt,
            APIQueryIntent
        )

    # ----------------------------------------
    # Node 2
    # ----------------------------------------
    def suggest_strategy(
        self,
        user_goal: str,
        weekly_hours: float,
        known_skills: list,
    ) -> StrategySuggestion:

        prompt = STRATEGY_PROMPT.format(
            user_goal=user_goal,
            weekly_hours=weekly_hours,
            known_skills=known_skills,
        )

        return self._cached_generate(
            prompt,
            StrategySuggestion
        )

    # ----------------------------------------
    # Node 3
    # ----------------------------------------
    def explain_roadmap(self, learning_roadmap) -> RoadmapExplanation:

        signature_data = [
            learning_roadmap.target_job_role,
            learning_roadmap.weekly_time_hours
        ]

        for step in learning_roadmap.steps:
            signature_data.append(step.skill_name)
            signature_data.append(step.mastery_level.value)
            signature_data.append(str(step.total_hours))

        roadmap_signature = hashlib.md5(
            "|".join(map(str, signature_data)).encode()
        ).hexdigest()

        if roadmap_signature in self.roadmap_cache:
            return self.roadmap_cache[roadmap_signature]

        phase_lines = []

        for step in learning_roadmap.steps:
            phase_lines.append(
                f"{step.skill_name} ({step.mastery_level.value}, {step.total_hours} hours)"
            )

        phase_summary = "\n".join(phase_lines)

        prompt = ROADMAP_EXPLANATION_PROMPT.format(
            target_job_role=learning_roadmap.target_job_role,
            weekly_hours=learning_roadmap.weekly_time_hours,
            phase_summary=phase_summary,
        )

        explanation = self.llm.generate_structured(
            prompt,
            RoadmapExplanation
        )

        self.roadmap_cache[roadmap_signature] = explanation

        return explanation

    # ----------------------------------------
    # Node 4
    # ----------------------------------------
    def generate_monitoring_feedback(
        self,
        metrics: dict,
        risk_profile: dict,
    ) -> MonitoringFeedback:

        prompt = MONITORING_PROMPT.format(
            metrics=metrics,
            risk_profile=risk_profile,
        )

        return self._cached_generate(
            prompt,
            MonitoringFeedback
        )

    # ----------------------------------------
    # Node 5
    # ----------------------------------------
    def generate_reflection_feedback(
        self,
        metrics: dict,
        risk_profile: dict,
        execution_summary: dict,
    ) -> ReflectionFeedback:

        prompt = REFLECTION_PROMPT.format(
            metrics=metrics,
            risk_profile=risk_profile,
            summary=execution_summary,
        )

        return self._cached_generate(
            prompt,
            ReflectionFeedback
        )

    # ----------------------------------------
    # Node 6
    # ----------------------------------------
    def rank_resources(self, aggregated_resources):

        jobs = [self._extract_title(j) for j in aggregated_resources.jobs[:10]]
        courses = [self._extract_title(c) for c in aggregated_resources.courses[:10]]
        projects = [self._extract_title(p) for p in aggregated_resources.projects[:10]]
        tutorials = [self._extract_title(t) for t in aggregated_resources.tutorials[:10]]

        jobs_str = "\n".join(jobs)
        courses_str = "\n".join(courses)
        projects_str = "\n".join(projects)
        tutorials_str = "\n".join(tutorials)

        prompt = RESOURCE_RANKING_PROMPT.format(
            skill=aggregated_resources.skill,
            jobs=jobs_str,
            courses=courses_str,
            projects=projects_str,
            tutorials=tutorials_str
        )

        return self._cached_generate(
            prompt,
            RankedResources
        )

    # ----------------------------------------
    # Node 7
    # ----------------------------------------
    def generate_resource_explanations(self, skill, ranked_resources):
        """
        Resource explanations are already generated during ranking.
        This step simply returns the ranked resources.
        """
        return ranked_resources

    # ----------------------------------------
    # Node 8
    # ----------------------------------------
    def generate_learning_plan(self, aggregated_resources, ranked_resources):

        prompt = LEARNING_PLAN_PROMPT.format(
            skill=aggregated_resources.skill,
            ranked_resources=ranked_resources
        )

        return self._cached_generate(
            prompt,
            LearningRecommendation
        )